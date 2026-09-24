"""DNF prediction baselines (vectorized)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.utils.frame import numeric_column


def historical_dnf_predict(task) -> pd.DataFrame:
    """Predict next-attempt DNF probability from historical person-event DNF rate."""
    if hasattr(task, "_features") and isinstance(task._features, pd.DataFrame) and len(task._features):
        feats = task._features.copy()
    else:
        feats = task.featurize(None)
    global_rate = float(task.data.frozen_stats.get("global_dnf_rate", 0.03))

    # merge frozen dnf rates
    stats = task.data.frozen_stats.get("person_event_stats", {}) or {}
    rows = []
    for k, v in stats.items():
        if isinstance(k, str) and "::" in k:
            pid, eid = k.split("::", 1)
        elif isinstance(k, (tuple, list)):
            pid, eid = str(k[0]), str(k[1])
        else:
            continue
        rows.append({"person_id": pid, "event_id": eid, "fs_dnf": v.get("dnf_rate", np.nan)})
    fs_df = pd.DataFrame(rows)
    if len(fs_df):
        feats = feats.merge(fs_df, on=["person_id", "event_id"], how="left")
    else:
        feats["fs_dnf"] = np.nan

    p = numeric_column(feats, "historical_dnf_rate")
    p = p.fillna(numeric_column(feats, "fs_dnf")).fillna(global_rate)

    if "target_dnf" in feats.columns:
        y = feats["target_dnf"]
    else:
        y = feats["best"] == -1

    return pd.DataFrame(
        {
            "result_id": feats.get("result_id"),
            "person_id": feats["person_id"].astype(str),
            "event_id": feats["event_id"].astype(str),
            "competition_id": feats.get("competition_id"),
            "round_type_id": feats.get("round_type_id"),
            "date": feats.get("date"),
            "y_true": pd.to_numeric(y, errors="coerce").fillna(0).astype(float),
            "y_pred": p.astype(float),
            "skill_level": feats.get("skill_level"),
            "time_slice": feats.get("time_slice"),
            "continent_id": feats.get("continent_id"),
            "is_cold_start": feats.get("is_cold_start"),
            "hard_uncertain": (p >= 0.1) & (p <= 0.3),
        }
    )
