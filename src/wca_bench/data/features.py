"""Vectorized feature engineering with mandatory as_of leakage guards."""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.schema import DNF, EVENT_FORMATS
from wca_bench.data.splits import assert_no_leakage, skill_level


def _prepare_results(results: pd.DataFrame) -> pd.DataFrame:
    df = results.copy()
    if "date" not in df.columns:
        if "start_date" not in df.columns:
            raise ValueError("results must contain start_date or date")
        df["date"] = pd.to_datetime(df["start_date"]).dt.date
    else:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    if "id" in df.columns and "result_id" not in df.columns:
        df["result_id"] = df["id"]
    return df


def build_result_features(
    results: pd.DataFrame,
    frozen_stats: dict[str, Any],
    *,
    as_of: date,
    history_window: int = 25,
    check_leakage: bool = True,
) -> pd.DataFrame:
    """Build per-result features using only rows strictly before as_of.

    Vectorized groupby aggregates on the history slice; no future data.
    """
    df = _prepare_results(results)
    history = df[df["date"] < as_of].copy()
    if check_leakage and len(history):
        assert_no_leakage(pd.Series(list(history["date"])), as_of)

    person_stats_raw = frozen_stats.get("person_event_stats", {})
    # normalize frozen keys to tuple form
    person_stats: dict[tuple[str, str], dict[str, float]] = {}
    for k, v in person_stats_raw.items():
        if isinstance(k, str) and "::" in k:
            pid, eid = k.split("::", 1)
            person_stats[(pid, eid)] = v
        elif isinstance(k, (tuple, list)) and len(k) == 2:
            person_stats[(str(k[0]), str(k[1]))] = v

    thresholds = frozen_stats.get("skill_thresholds", {})
    global_dnf = float(frozen_stats.get("global_dnf_rate", 0.03))
    continent_map = frozen_stats.get("continent_map", {})

    out = df.copy()
    out["result_id"] = out["result_id"] if "result_id" in out.columns else out.get("id")
    out["person_id"] = out["person_id"].astype(str)
    out["event_id"] = out["event_id"].astype(str)

    if history.empty:
        for col, default in [
            ("n_hist_rounds", 0),
            ("n_hist_valid", 0),
            ("n_competitions_hist", 0),
            ("recent_mean", np.nan),
            ("recent_std", np.nan),
            ("recent_min", np.nan),
            ("recent_slope", 0.0),
            ("historical_dnf_rate", global_dnf),
            ("recent_dnf_count", 0),
            ("days_since_last", -1),
        ]:
            out[col] = default
        out["is_cold_start"] = True
        out["as_of"] = as_of
        return _finalize_features(out, person_stats, thresholds, continent_map)

    h = history.copy()
    h["person_id"] = h["person_id"].astype(str)
    h["event_id"] = h["event_id"].astype(str)
    h["is_valid"] = h["best"] > 0
    h["is_dnf"] = h["best"] == DNF
    h["best_num"] = np.where(h["is_valid"], h["best"].astype(float), np.nan)

    # person-event history aggregates
    pe = h.groupby(["person_id", "event_id"], sort=False)
    pe_agg = pe.agg(
        n_hist_rounds=("best", "size"),
        n_hist_valid=("is_valid", "sum"),
        historical_dnf_rate=("is_dnf", "mean"),
        recent_min=("best_num", "min"),
    ).reset_index()

    # recent window mean/std/slope using last N valid scores
    def _recent_stats(g: pd.DataFrame) -> pd.Series:
        vals = g.loc[g["is_valid"], "best_num"].tail(history_window)
        if len(vals) >= 3:
            x = np.arange(len(vals))
            slope = float(np.polyfit(x, vals.to_numpy(dtype=float), 1)[0])
        else:
            slope = 0.0
        if len(vals) >= 1:
            mean = float(vals.mean())
        else:
            mean = np.nan
        std = float(vals.std(ddof=0)) if len(vals) > 1 else 0.0
        return pd.Series({"recent_mean": mean, "recent_std": std, "recent_slope": slope})

    recent = pe.apply(_recent_stats, include_groups=False).reset_index()  # type: ignore[call-overload]
    pe_agg = pe_agg.merge(recent, on=["person_id", "event_id"], how="left")

    # recent DNF count in last 10 rounds
    recent_dnf = (
        pe.apply(lambda g: float(g["is_dnf"].tail(10).sum()), include_groups=False)  # type: ignore[call-overload]
        .reset_index(name="recent_dnf_count")
    )
    pe_agg = pe_agg.merge(recent_dnf, on=["person_id", "event_id"], how="left")

    # person-level competition count and last date
    p_all = h.groupby("person_id", sort=False)
    p_agg = p_all.agg(
        n_competitions_hist=("competition_id", "nunique"),
        last_date=("date", "max"),
    ).reset_index()
    p_agg["days_since_last"] = p_agg["last_date"].apply(lambda d: (as_of - d).days)

    out = out.merge(pe_agg, on=["person_id", "event_id"], how="left")
    out = out.merge(
        p_agg[["person_id", "n_competitions_hist", "days_since_last"]],
        on="person_id",
        how="left",
    )

    # opponent count from history for same competition-event-round
    peers = (
        h.groupby(["competition_id", "event_id", "round_type_id"], dropna=False)
        .size()
        .reset_index(name="n_opponents_hist")
    )
    out = out.merge(peers, on=["competition_id", "event_id", "round_type_id"], how="left")

    out["n_hist_rounds"] = out["n_hist_rounds"].fillna(0).astype(int)
    out["n_hist_valid"] = out["n_hist_valid"].fillna(0).astype(int)
    out["n_competitions_hist"] = out["n_competitions_hist"].fillna(0).astype(int)
    out["historical_dnf_rate"] = out["historical_dnf_rate"].fillna(global_dnf)
    out["recent_dnf_count"] = out["recent_dnf_count"].fillna(0)
    out["n_opponents_hist"] = out["n_opponents_hist"].fillna(0).astype(int)
    out["days_since_last"] = out["days_since_last"].fillna(-1).astype(int)
    out["is_cold_start"] = out["n_hist_rounds"] == 0
    out["as_of"] = as_of
    return _finalize_features(out, person_stats, thresholds, continent_map)


def _finalize_features(
    out: pd.DataFrame,
    person_stats: dict,
    thresholds: dict,
    continent_map: dict,
) -> pd.DataFrame:
    # frozen train-period stats via merge instead of row-wise apply
    pe_rows = []
    for k, v in person_stats.items():
        if isinstance(k, str) and "::" in k:
            pid, eid = k.split("::", 1)
        else:
            pid, eid = k
        pe_rows.append(
            {
                "person_id": str(pid),
                "event_id": str(eid),
                "frozen_mean": v.get("mean_best", np.nan),
                "frozen_std": v.get("std_best", np.nan),
                "frozen_best": v.get("best", np.nan),
            }
        )
    pe_fs = pd.DataFrame(pe_rows)
    if len(pe_fs):
        out = out.drop(columns=[c for c in ["frozen_mean", "frozen_std", "frozen_best"] if c in out.columns], errors="ignore")
        out = out.merge(pe_fs, on=["person_id", "event_id"], how="left")
    else:
        out["frozen_mean"] = np.nan
        out["frozen_std"] = np.nan
        out["frozen_best"] = np.nan

    # prefer recent stats when available, else frozen
    out["recent_mean"] = out["recent_mean"].fillna(out["frozen_mean"])
    out["recent_std"] = out["recent_std"].fillna(out["frozen_std"])
    out["recent_min"] = out["recent_min"].fillna(out["frozen_best"])
    out["recent_slope"] = out["recent_slope"].fillna(0.0)

    if "continent_id" not in out.columns:
        out["continent_id"] = out["person_id"].map(lambda p: continent_map.get(str(p), "UNKNOWN"))
    out["skill_level"] = [
        skill_level(
            r["recent_mean"] if pd.notna(r.get("recent_mean")) else r.get("frozen_best"),
            r["event_id"],
            thresholds,
        )
        for _, r in out.iterrows()
    ]
    out["event_format"] = out["event_id"].map(lambda e: EVENT_FORMATS.get(e, {}).get("format", "time"))
    return out


def build_competition_features(
    features: pd.DataFrame,
    frozen_stats: dict[str, Any],
) -> pd.DataFrame:
    """Attach competition-level aggregates from precomputed features."""
    if features.empty:
        return features.copy()
    keys = ["competition_id", "event_id", "round_type_id"]
    g = (
        features.groupby(keys, dropna=False)
        .agg(
            n_starters=("person_id", "nunique"),
            mean_recent_mean=("recent_mean", "mean"),
            std_recent_mean=("recent_mean", "std"),
            mean_dnf_rate=("historical_dnf_rate", "mean"),
        )
        .reset_index()
    )
    g["field_strength"] = g["mean_recent_mean"]
    return features.merge(g, on=keys, how="left")


def build_sequence(
    features: pd.DataFrame,
    person_id: str,
    event_id: str,
    as_of: date,
    n: int = 25,
) -> list[float]:
    """Return last-n valid historical scores for a person-event before as_of."""
    df = features.copy()
    if "date" in df.columns:
        df = df[(df["person_id"] == person_id) & (df["event_id"] == event_id)]
        df = df[df["date"] < as_of]
        vals = df.loc[df["best"] > 0, "best"].astype(float).tolist()
        return vals[-n:]
    return []
