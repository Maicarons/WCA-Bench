"""Hierarchical (empirical-Bayes) human-limit estimation across events."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.splits import TRAIN_END


def _train_window(series: pd.DataFrame, train_end) -> pd.DataFrame:
    s = series.copy()
    if len(s):
        s["date"] = pd.to_datetime(s["date"])
        s = s[s["date"].dt.date <= train_end]
    return s


def _log_linear_ratio(s: pd.DataFrame, *, horizon_years: float) -> tuple[float, float, float]:
    """Return (ratio, year_converge, log_slope) for one event series.

    Fits log(value) ~ a + b * t and extrapolates ``horizon_years`` beyond the
    last observation. ``ratio`` = predicted limit / last value (in (0, 1]).
    """
    y = np.log(s["value"].to_numpy(dtype=float))
    t = (pd.to_datetime(s["date"]) - pd.to_datetime(s["date"]).min()).dt.days.to_numpy(dtype=float) / 365.25
    if len(s) < 3 or np.allclose(t, t[0]):
        return float("nan"), float("nan"), float("nan")
    slope, intercept = np.polyfit(t, y, 1)
    t_end = float(t[-1])
    t_h = t_end + horizon_years
    log_limit = intercept + slope * t_h
    last = float(s["value"].iloc[-1])
    ratio = float(np.exp(log_limit) / last)
    ratio = float(np.clip(ratio, 0.0, 1.0))
    year_converge = float("nan")
    if slope < 0:
        eps = 0.005
        log_target = np.log((1 - eps) * last) if ratio <= 0 else log_limit - np.log(1 / max(ratio, 1e-9))
        t_star = (log_target - intercept) / slope
        start_year = pd.to_datetime(s["date"].min()).year
        year_converge = float(start_year + max(t_star, 0.0) / 1.0)
    return ratio, year_converge, float(slope)


def hierarchical_limit_estimate(
    task,
    *,
    train_end: Any = TRAIN_END,
    kappa: float = 4.0,
    horizon_years: float = 5.0,
) -> pd.DataFrame:
    """Cross-event shrinkage of extrapolated improvement ratios.

    Each event is first extroplated on its own scale (log-linear trend) to a
    relative limit ratio. These ratios are then shrunk toward the pooled mean
    with an empirical-Bayes weight ``kappa`` so sparse events borrow information
    from well-observed ones. Stability is reported as the leave-one-out spread
    of the shrunk limit.
    """
    series_map: dict[str, pd.DataFrame] = getattr(task, "_series", {}) or {}
    rows: list[dict[str, Any]] = []
    raw: dict[str, dict[str, Any]] = {}

    for eid, series in series_map.items():
        s = _train_window(series, train_end)
        if len(s) < 3:
            raw[str(eid)] = {"ratio": float("nan"), "last": np.nan, "year": float("nan"), "slope": float("nan")}
            continue
        s = s.sort_values("date")
        ratio, year, slope = _log_linear_ratio(s, horizon_years=horizon_years)
        raw[str(eid)] = {
            "ratio": ratio,
            "last": float(s["value"].iloc[-1]),
            "year": year,
            "slope": slope,
            "series": s,
        }

    valid_ratios = [v["ratio"] for v in raw.values() if np.isfinite(v["ratio"])]
    pooled = float(np.mean(valid_ratios)) if valid_ratios else float("nan")

    for eid, info in raw.items():
        s = info.get("series")
        if s is None or not np.isfinite(info["ratio"]):
            rows.append(
                {
                    "event_id": eid,
                    "limit": float("nan"),
                    "year_converge": float("nan"),
                    "n_points": 0 if s is None else int(len(s)),
                    "loo_std": float("nan"),
                    "method": "hierarchical_shrinkage",
                }
            )
            continue
        n = int(len(s))
        if np.isfinite(pooled):
            ratio_hat = (n * info["ratio"] + kappa * pooled) / (n + kappa)
        else:
            ratio_hat = info["ratio"]
        limit = float(ratio_hat * info["last"])

        loo = []
        for i in range(n):
            sub = s.drop(index=s.index[i])
            if len(sub) < 3:
                continue
            r, _, _ = _log_linear_ratio(sub, horizon_years=horizon_years)
            if np.isfinite(r):
                loo.append(float(r * info["last"]))
        loo_std = float(np.std(loo)) if len(loo) > 1 else float("nan")

        rows.append(
            {
                "event_id": eid,
                "limit": limit,
                "year_converge": info["year"],
                "n_points": n,
                "loo_std": loo_std,
                "slope": info["slope"],
                "ratio": float(ratio_hat),
                "pooled_ratio": pooled,
                "method": "hierarchical_shrinkage",
            }
        )
    return pd.DataFrame(rows)
