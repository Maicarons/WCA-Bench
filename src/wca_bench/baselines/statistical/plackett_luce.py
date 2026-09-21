"""Plackett-Luce / psych-sheet placement baselines (vectorized)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.history_mean import history_mean_predict


def psych_sheet_predict(task) -> pd.DataFrame:
    """Rank competitors within each competition-event-round by predicted score."""
    preds = history_mean_predict(task)
    if preds.empty:
        return preds
    gcols = [c for c in ["competition_id", "event_id", "round_type_id"] if c in preds.columns]
    if not gcols:
        gcols = ["competition_id"]
    out = preds.copy()
    out["y_pred_rank"] = out.groupby(gcols)["y_pred"].rank(ascending=True, method="average")
    out["y_true_rank"] = out.groupby(gcols)["y_true"].rank(ascending=True, method="average")
    out["podium_true"] = out["y_true_rank"] <= 3
    out["podium_pred"] = out["y_pred_rank"] <= 3
    return out


def kde_simulate_placement(task, n_sim: int = 30, seed: int = 7) -> pd.DataFrame:
    """Monte-Carlo ranking by sampling around predicted means."""
    rng = np.random.default_rng(seed)
    preds = psych_sheet_predict(task)
    if preds.empty:
        return preds
    gcols = [c for c in ["competition_id", "event_id", "round_type_id"] if c in preds.columns]
    out = preds.copy()
    std = pd.to_numeric(out.get("recent_std"), errors="coerce")
    if std is None:
        std = pd.Series(np.abs(out["y_pred"]) * 0.08, index=out.index)
    std = std.fillna(pd.Series(np.abs(out["y_pred"]) * 0.08, index=out.index))
    std = std.clip(lower=1e-6)

    p_podium = np.zeros(len(out), dtype=float)
    # sample within groups for rank uncertainty
    for _, idx in out.groupby(gcols, sort=False).groups.items():
        idx = list(idx)
        mu = out.loc[idx, "y_pred"].to_numpy(dtype=float)
        sd = std.loc[idx].to_numpy(dtype=float)
        sims = rng.normal(mu, sd, size=(n_sim, len(idx)))
        # lower score better
        order = np.argsort(sims, axis=1)
        ranks = np.empty_like(order)
        ranks[np.arange(n_sim)[:, None], order] = np.arange(1, len(idx) + 1)
        p_podium[out.index.get_indexer(idx)] = (ranks <= 3).mean(axis=0)
    out["p_podium"] = p_podium
    return out


def plackett_luce_scores(task) -> pd.DataFrame:
    """Score competitors by inverse predicted time as Plackett-Luce utilities."""
    preds = psych_sheet_predict(task)
    if preds.empty:
        return preds
    out = preds.copy()
    out["pl_utility"] = -np.log(out["y_pred"].clip(lower=1e-6))
    gcols = [c for c in ["competition_id", "event_id", "round_type_id"] if c in out.columns]
    out["y_pred_rank"] = out.groupby(gcols)["pl_utility"].rank(ascending=False)
    out["y_true_rank"] = out.groupby(gcols)["y_true"].rank(ascending=True)
    return out
