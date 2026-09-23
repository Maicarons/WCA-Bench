"""Beta-Binomial shrinkage DNF baseline (closed form, no third-party Bayes deps)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.utils.frame import numeric_column


def beta_binomial_dnf_predict(
    task,
    *,
    prior_strength: float = 8.0,
) -> pd.DataFrame:
    """Shrink person-event DNF rates toward the global rate via a Beta prior.

    The posterior mean is ``(k + alpha) / (n + alpha + beta)`` where ``k``/``n``
    come from the person-event history and the prior is centred on the global
    train-period DNF rate with total pseudo-count ``prior_strength``. This is a
    closed-form empirical-Bayes estimator and requires no probabilistic library.
    """
    feats = (
        task._features
        if hasattr(task, "_features") and task._features is not None
        else task.featurize(None)
    )
    feats = feats.copy() if isinstance(feats, pd.DataFrame) else pd.DataFrame()
    if feats.empty:
        return feats

    global_rate = float(task.data.frozen_stats.get("global_dnf_rate", 0.03))
    global_rate = float(np.clip(global_rate, 1e-4, 1 - 1e-4))
    alpha0 = global_rate * prior_strength
    beta0 = (1.0 - global_rate) * prior_strength

    rate = numeric_column(feats, "historical_dnf_rate")
    rounds = numeric_column(feats, "n_hist_rounds")
    rate = rate.fillna(global_rate)
    rounds = rounds.fillna(0).clip(lower=0)

    k = rate * rounds
    post = (k + alpha0) / (rounds + alpha0 + beta0)
    # rows without history collapse to the prior mean (= global rate)
    post = post.where(rounds > 0, global_rate)
    post = post.clip(1e-6, 1.0 - 1e-6)

    out = feats.copy()
    out["y_true"] = feats.get("target_dnf", pd.Series(np.nan, index=feats.index))
    out["y_pred"] = post.astype(float)
    out["hard_uncertain"] = (out["y_pred"] >= 0.1) & (out["y_pred"] <= 0.3)
    return out
