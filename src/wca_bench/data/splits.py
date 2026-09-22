"""Time-based train/val/test splits and frozen statistics."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.schema import DNF, EVENT_FORMATS

TRAIN_START = date(2003, 1, 1)
TRAIN_END = date(2022, 12, 31)
VAL_START = date(2023, 1, 1)
VAL_END = date(2024, 12, 31)
TEST_START = date(2025, 1, 1)
TEST_END = date(2026, 12, 31)

TIME_SLICES: dict[str, tuple[date, date]] = {
    "train": (TRAIN_START, TRAIN_END),
    "val": (VAL_START, VAL_END),
    "test": (TEST_START, TEST_END),
    "test_a": (date(2025, 1, 1), date(2025, 6, 30)),
    "test_b": (date(2025, 7, 1), date(2025, 12, 31)),
    "test_c": (date(2026, 1, 1), date(2026, 6, 30)),
}


def _to_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return pd.to_datetime(value).date()


def assign_split(dates: Any) -> pd.Series:
    """Map dates to split labels: train / val / test / out_of_window."""
    s = pd.to_datetime(pd.Series(dates)).dt.date
    out = []
    for d in s:
        if d is None or (isinstance(d, float) and np.isnan(d)):
            out.append("out_of_window")
            continue
        if TRAIN_START <= d <= TRAIN_END:
            out.append("train")
        elif VAL_START <= d <= VAL_END:
            out.append("val")
        elif TEST_START <= d <= TEST_END:
            out.append("test")
        else:
            out.append("out_of_window")
    return pd.Series(out, index=pd.Series(dates).index, name="split")


def time_slice(dates: Any) -> pd.Series:
    """Map dates to Test-A/B/C when inside the test window, else the split name."""
    split = assign_split(dates)
    s = pd.to_datetime(pd.Series(dates)).dt.date
    out = []
    for d, sp in zip(s, split, strict=False):
        if sp != "test":
            out.append(sp)
            continue
        for name, (lo, hi) in (("test_a", TIME_SLICES["test_a"]), ("test_b", TIME_SLICES["test_b"]), ("test_c", TIME_SLICES["test_c"])):
            if lo <= d <= hi:
                out.append(name)
                break
        else:
            out.append("test_extended")
    return pd.Series(out, index=pd.Series(dates).index, name="time_slice")


def freeze_stats(results: pd.DataFrame, persons: pd.DataFrame | None = None) -> dict[str, Any]:
    """Compute frozen benchmark statistics from training-period data only."""
    df = results.copy()
    if "date" not in df.columns and "start_date" in df.columns:
        df["date"] = pd.to_datetime(df["start_date"]).dt.date
    df["date"] = pd.to_datetime(df["date"]).dt.date
    train = df[df["date"] <= TRAIN_END].copy()
    train = train.assign(split="train")

    # Person-event means on valid numeric values
    person_stats: dict[tuple[str, str], dict[str, float]] = {}
    for (pid, eid), g in train.groupby(["person_id", "event_id"], sort=False):
        scores = g.loc[(g["best"] > 0), "best"].astype(float)
        dnfs = g.loc[g["best"] == DNF, "best"]
        if len(scores) == 0:
            continue
        person_stats[(str(pid), str(eid))] = {
            "mean_best": float(scores.mean()),
            "std_best": float(scores.std(ddof=0)),
            "n_attempts": float(len(g)),
            "best": float(scores.min()),
            "dnf_rate": float(len(dnfs) / max(len(g), 1)),
        }

    # Event world-record (minimum positive best) in train window
    wr: dict[str, float] = {}
    for eid, g in train.groupby("event_id"):
        pos = g.loc[g["best"] > 0, "best"].astype(float)
        if len(pos):
            wr[str(eid)] = float(pos.min())

    # Skill thresholds per event from train bests (lower is better)
    skill_thresholds: dict[str, dict[str, float]] = {}
    for eid, g in train.groupby("event_id"):
        pos = g.loc[g["best"] > 0, "best"].astype(float)
        if len(pos) < 5:
            continue
        skill_thresholds[str(eid)] = {
            "p05": float(pos.quantile(0.05)),  # elite
            "p25": float(pos.quantile(0.25)),
            "p50": float(pos.quantile(0.50)),
            "p75": float(pos.quantile(0.75)),
        }

    # Continent mapping
    continent_map: dict[str, str] = {}
    if persons is not None and "continent_id" in persons.columns:
        for _, row in persons.iterrows():
            continent_map[str(row["wca_id"])] = str(row.get("continent_id", "UNKNOWN"))

    # Global DNF rate
    valid_mask = train["best"].isin([DNF]) | train["best"].gt(0)
    global_dnf = float((train["best"] == DNF).sum() / max(valid_mask.sum(), 1))

    return {
        "frozen_at": TRAIN_END.isoformat(),
        "person_event_stats": person_stats,
        "world_records": wr,
        "skill_thresholds": skill_thresholds,
        "continent_map": continent_map,
        "global_dnf_rate": global_dnf,
        "n_train_rows": int(len(train)),
        "slices": {k: {"start": lo.isoformat(), "end": hi.isoformat()} for k, (lo, hi) in TIME_SLICES.items()},
    }


def skill_level(value: float | int | None, event_id: str, thresholds: dict) -> str:
    """Classify skill level using frozen train quantiles (lower time is better)."""
    if value is None or (isinstance(value, (int, float)) and value <= 0):
        return "unknown"
    thr = thresholds.get(event_id)
    if not thr:
        return "unknown"
    v = float(value)
    if v <= thr["p05"]:
        return "elite"
    if v <= thr["p25"]:
        return "advanced"
    if v <= thr["p75"]:
        return "intermediate"
    return "novice"


def assert_no_leakage(feature_dates: Any, target_date: Any) -> None:
    """Assert all feature timestamps are strictly before target_date."""
    target = _to_date(target_date)
    dates = pd.to_datetime(pd.Series(feature_dates)).dt.date
    bad = dates[dates >= target]
    if len(bad):
        raise AssertionError(
            f"Leakage detected: {len(bad)} feature dates >= target {target.isoformat()}"
        )


def event_format(event_id: str) -> str:
    return EVENT_FORMATS.get(event_id, {}).get("format", "time")
