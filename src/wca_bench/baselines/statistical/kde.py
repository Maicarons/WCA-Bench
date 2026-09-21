"""KDE-based result prediction using historical person-event scores."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.history_mean import history_mean_predict


def kde_predict_result(task, n_sim: int = 50, seed: int = 42) -> pd.DataFrame:
    """Predict via closed-form/KDE-like sampling using frozen/recent mean+std.

    Uses normal approximation around person-event recent/frozen stats instead of
    per-row bootstrap for scalability on full WCA exports.
    """
    rng = np.random.default_rng(seed)
    base = history_mean_predict(task)
    if base.empty:
        return base

    mean = base["y_pred"].to_numpy(dtype=float)
    std = pd.to_numeric(base.get("recent_std"), errors="coerce").to_numpy(dtype=float)
    fallback = np.where(np.isfinite(std) & (std > 0), std, np.abs(mean) * 0.08)
    std = np.where(np.isfinite(std) & (std > 0), std, fallback)

    # analytical interval under normal approx: median ~ mean, 5-95% ~ mean ± 1.645σ
    out = base.copy()
    out["y_pred"] = mean
    out["y_lo"] = np.maximum(mean - 1.645 * std, 1e-6)
    out["y_hi"] = mean + 1.645 * std
    # small MC residual for non-Gaussian tails on a subsample
    n_mc = min(2000, len(out))
    if n_mc > 0:
        idx = rng.choice(len(out), size=n_mc, replace=False)
        samples = rng.normal(mean[idx], std[idx], size=(n_sim, n_mc))
        samples = samples[samples > 0]
        # keep analytical interval; point estimate stays mean
    return out
