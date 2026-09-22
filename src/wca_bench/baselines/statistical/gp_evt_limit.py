"""Gaussian-process trend + extreme-value tail limit estimation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.splits import TRAIN_END


def _rbf_gp_posterior(
    t: np.ndarray, y: np.ndarray, t_star: np.ndarray, lengthscale: float, noise: float
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Closed-form GP posterior (mean, std, used_jitter) with an RBF kernel."""

    def k(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        d = a[:, None] - b[None, :]
        return np.exp(-0.5 * (d / lengthscale) ** 2)

    K = k(t, t) + noise * np.eye(len(t))
    Ks = k(t_star, t)
    Kss = k(t_star, t_star)
    used_jitter = False
    try:
        L = np.linalg.cholesky(K)
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, y))
        mean = Ks @ alpha
        v = np.linalg.solve(L, Ks.T)
        cov = Kss - v.T @ v
    except np.linalg.LinAlgError:
        used_jitter = True
        jitter = 1e-6
        K = K + jitter * np.eye(len(t))
        alpha = np.linalg.solve(K, y)
        mean = Ks @ alpha
        cov = Kss - Ks @ np.linalg.solve(K, Ks.T)
    var = np.clip(np.diag(cov), 0.0, None)
    return mean, np.sqrt(var), used_jitter


def _gpd_return_level(excesses: np.ndarray, q: float = 0.99) -> float:
    """Method-of-moments Generalized Pareto return level for positive excesses."""
    ex = np.asarray(excesses, dtype=float)
    ex = ex[np.isfinite(ex) & (ex > 0)]
    if len(ex) < 5:
        return float("nan")
    mean = float(ex.mean())
    var = float(ex.var())
    if var <= 0 or mean <= 0:
        return float("nan")
    xi = 0.5 * (1.0 - mean * mean / var)
    sigma = 0.5 * mean * (mean * mean / var + 1.0)
    if abs(xi) < 1e-6:
        return float(sigma * np.log(1.0 / (1.0 - q)))
    return float(sigma / xi * ((1.0 - q) ** (-xi) - 1.0))


def gp_evt_limit_estimate(
    task,
    *,
    train_end: Any = TRAIN_END,
    horizon_years: float = 6.0,
    evt_quantile: float = 0.99,
) -> pd.DataFrame:
    """GP trend extrapolation refined by an extreme-value tail return level.

    A numpy RBF Gaussian process is fit to log(world-record) versus time; the
    predictive mean at the horizon gives a smooth trend limit while the GPD
    return level of historical log-improvements provides a conservative tail
    adjustment. The reported stability is the GP posterior standard deviation.
    """

    series_map: dict[str, pd.DataFrame] = getattr(task, "_series", {}) or {}
    rows: list[dict[str, Any]] = []
    jitter_events: list[str] = []
    for eid, series in series_map.items():
        s = series.copy()
        if len(s):
            s["date"] = pd.to_datetime(s["date"])
            s = s[s["date"].dt.date <= train_end].sort_values("date")
        if len(s) < 5:
            rows.append(
                {
                    "event_id": str(eid),
                    "limit": float("nan"),
                    "year_converge": float("nan"),
                    "n_points": int(len(s)),
                    "loo_std": float("nan"),
                    "method": "gp_evt",
                }
            )
            continue

        t = (
            pd.to_datetime(s["date"]) - pd.to_datetime(s["date"]).min()
        ).dt.days.to_numpy(dtype=float) / 365.25
        y = np.log(s["value"].to_numpy(dtype=float))
        dt = np.diff(t)
        ls = float(np.median(dt[dt > 0])) if np.any(dt > 0) else 1.0
        ls = max(ls * 2.5, 0.5)
        t_h = t[-1] + horizon_years
        t_star = np.array([t_h])
        mean, std, used_jitter = _rbf_gp_posterior(t, y, t_star, ls, noise=1e-3)
        if used_jitter:
            jitter_events.append(str(eid))
        gp_limit = float(np.exp(mean[0]))

        last = float(s["value"].iloc[-1])
        improvements = -np.diff(y)  # positive when records improve
        tail = _gpd_return_level(improvements, q=evt_quantile)
        evt_limit = float(np.exp(y[-1] - tail)) if np.isfinite(tail) else float("nan")

        if np.isfinite(evt_limit):
            limit = float(max(gp_limit, evt_limit))
        else:
            limit = gp_limit
        limit = float(min(limit, last))

        year_converge = float("nan")
        if limit < last:
            year_converge = float(pd.to_datetime(s["date"].max()).year + horizon_years)

        rows.append(
            {
                "event_id": str(eid),
                "limit": limit,
                "gp_limit": gp_limit,
                "evt_limit": evt_limit,
                "year_converge": year_converge,
                "n_points": int(len(s)),
                "loo_std": float(std[0]),
                "gp_jitter": bool(used_jitter),
                "method": "gp_evt",
            }
        )
    out = pd.DataFrame(rows)
    if jitter_events:
        out.attrs["fallback"] = "cholesky_jitter"
        out.attrs["fallback_reason"] = (
            "Cholesky failed; added 1e-6 jitter for events: " + ", ".join(jitter_events)
        )
    return out
