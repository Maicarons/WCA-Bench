"""Human-limit estimation baselines (vectorized WR series + fast fits)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def build_world_record_series(results: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract running world-record time series per event from results."""
    df = results.copy()
    if "date" not in df.columns:
        if "start_date" not in df.columns:
            return {}
        df["date"] = pd.to_datetime(df["start_date"]).dt.date
    df["date"] = pd.to_datetime(df["date"])
    df = df[pd.to_numeric(df["best"], errors="coerce") > 0]
    if df.empty:
        return {}
    df["best"] = df["best"].astype(float)
    series: dict[str, pd.DataFrame] = {}
    for eid, g in df.groupby("event_id"):
        g = g.sort_values(["date", "best"])
        # running minimum
        g = g.copy()
        g["wr"] = g["best"].cummin()
        # keep only improvement points
        prev = g["wr"].shift()
        imp = g[g["wr"] < prev.fillna(np.inf)]
        if imp.empty:
            imp = g.nsmallest(1, "best")
        series[str(eid)] = pd.DataFrame(
            {"date": imp["date"].dt.date, "value": imp["wr"].astype(float)}
        )
    return series


def exponential_limit_estimate(
    series: pd.DataFrame,
    *,
    min_points: int = 5,
    skip_loo: bool = False,
) -> dict[str, Any]:
    """Fit y(t) = L + (y0 - L) * exp(-lambda * t) via coarse grid + least squares."""
    if series is None or len(series) < min_points:
        return {
            "limit": float("nan"),
            "lambda": float("nan"),
            "year_converge": float("nan"),
            "n_points": 0 if series is None else int(len(series)),
            "method": "exponential_decay",
        }
    s = series.copy()
    s["t"] = (pd.to_datetime(s["date"]) - pd.to_datetime(s["date"]).min()).dt.days / 365.25
    t = s["t"].to_numpy(dtype=float)
    y = s["value"].to_numpy(dtype=float)
    y0 = float(y[0])
    y_min = float(y.min())

    best = {"sse": np.inf, "limit": y_min, "lambda": 0.1}
    # smaller grid for speed
    for L in np.linspace(max(y_min * 0.25, 0.05 * y_min), y_min * 0.995, 12):
        for lam in np.linspace(0.05, 1.5, 12):
            pred = L + (y0 - L) * np.exp(-lam * t)
            sse = float(np.sum((pred - y) ** 2))
            if sse < best["sse"]:
                best = {"sse": sse, "limit": float(L), "lambda": float(lam)}

    L = best["limit"]
    lam = best["lambda"]
    start = pd.to_datetime(s["date"].min())
    t_conv = np.inf
    if y0 > L and lam > 0:
        thr = 0.005 / lam
        if thr > 0:
            t_conv = -np.log(thr) / lam
    year_converge = start.year + t_conv if np.isfinite(t_conv) else float("nan")

    stability = float("nan")
    if (not skip_loo) and len(s) >= 8:
        estimates = []
        idxs = list(range(0, len(s), max(1, len(s) // 6)))[:6]
        for i in idxs:
            sub = s.drop(index=s.index[i])
            est = exponential_limit_estimate(sub, min_points=min_points, skip_loo=True)
            if np.isfinite(est["limit"]):
                estimates.append(est["limit"])
        stability = float(np.std(estimates)) if estimates else float("nan")

    return {
        "limit": float(L),
        "lambda": float(lam),
        "year_converge": float(year_converge),
        "n_points": int(len(s)),
        "sse": float(best["sse"]),
        "loo_std": stability,
        "method": "exponential_decay",
        "last_wr": float(y[-1]),
    }


def changepoint_limit_estimate(series: pd.DataFrame) -> dict[str, Any]:
    """Simple segmented trend: estimate limit from last-segment slope extrapolation."""
    if series is None or len(series) < 6:
        return {"limit": float("nan"), "year_converge": float("nan"), "n_points": 0}
    s = series.copy()
    s["t"] = (pd.to_datetime(s["date"]) - pd.to_datetime(s["date"].min())).dt.days / 365.25
    t = s["t"].to_numpy(dtype=float)
    y = s["value"].to_numpy(dtype=float)
    mid = np.median(t)
    left = t <= mid
    right = t > mid
    if right.sum() < 2 or left.sum() < 2:
        return {"limit": float(y[-1]), "year_converge": float("nan"), "n_points": len(s)}
    slope_right = float(np.polyfit(t[right], y[right], 1)[0])
    last = float(y[-1])
    if slope_right >= 0:
        limit = last
    else:
        limit = max(last * 0.75, last + slope_right * 5)
    return {
        "limit": float(limit),
        "slope_last_half": slope_right,
        "year_converge": float("nan"),
        "n_points": int(len(s)),
        "method": "changepoint",
    }
