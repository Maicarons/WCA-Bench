"""Trivial/history-mean baseline for result prediction (vectorized)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _person_stats_frame(task) -> pd.DataFrame:
    stats = task.data.frozen_stats.get("person_event_stats", {}) or {}
    rows = []
    for k, v in stats.items():
        if isinstance(k, str) and "::" in k:
            pid, eid = k.split("::", 1)
        elif isinstance(k, (tuple, list)) and len(k) == 2:
            pid, eid = str(k[0]), str(k[1])
        else:
            continue
        rows.append(
            {
                "person_id": pid,
                "event_id": eid,
                "fs_mean": v.get("mean_best", np.nan),
                "fs_std": v.get("std_best", np.nan),
                "fs_best": v.get("best", np.nan),
                "fs_dnf_rate": v.get("dnf_rate", np.nan),
            }
        )
    return pd.DataFrame(rows)


def history_mean_predict(task, window: int = 25) -> pd.DataFrame:
    """Predict best/average by recent/frozen historical mean; fallback to global."""
    if hasattr(task, "_features") and isinstance(task._features, pd.DataFrame) and len(task._features):
        df = task._features.copy()
    else:
        df = task.featurize(None)

    fs_df = _person_stats_frame(task)
    global_means = fs_df["fs_mean"].dropna() if len(fs_df) else pd.Series(dtype=float)
    gmean = float(global_means.mean()) if len(global_means) else 1000.0

    if len(fs_df):
        df = df.merge(fs_df, on=["person_id", "event_id"], how="left")
    else:
        df["fs_mean"] = np.nan
        df["fs_dnf_rate"] = np.nan
        df["fs_best"] = np.nan
        df["fs_std"] = np.nan

    y_pred = df["recent_mean"].astype(float)
    y_pred = y_pred.fillna(df["fs_mean"]).fillna(gmean)

    best = pd.to_numeric(df.get("best"), errors="coerce")
    average = pd.to_numeric(df.get("average"), errors="coerce")

    out = pd.DataFrame(
        {
            "result_id": df.get("result_id"),
            "person_id": df["person_id"].astype(str),
            "event_id": df["event_id"].astype(str),
            "competition_id": df.get("competition_id"),
            "round_type_id": df.get("round_type_id"),
            "date": df.get("date"),
            "y_true": best.where(best > 0),
            "y_pred": y_pred,
            "y_true_avg": average.where(average > 0),
            "y_pred_avg": y_pred,
            "skill_level": df.get("skill_level"),
            "time_slice": df.get("time_slice"),
            "continent_id": df.get("continent_id"),
            "is_cold_start": df.get("is_cold_start"),
            "recent_mean": df.get("recent_mean"),
            "recent_std": df.get("recent_std"),
            "historical_dnf_rate": df.get("historical_dnf_rate"),
        }
    )
    return out
