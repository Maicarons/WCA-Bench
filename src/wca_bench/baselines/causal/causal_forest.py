"""Causal-forest / honest-split T-learner skill transfer estimator."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.schema import EVENT_FORMATS


def _pair_level_frame(dst: pd.DataFrame, src: pd.DataFrame, person_first, event_from: str):
    """Build person-level (treatment, outcome, covariates) rows for one event pair."""
    rows = []
    for pid, g in dst.groupby("person_id"):
        if len(g) < 2:
            continue
        t0 = g["date"].min()
        post = g[g["date"] > t0]
        if len(post) < 1:
            continue
        src_hist = src[(src["person_id"] == pid) & (src["date"] < t0)]
        d = 1.0 if len(src_hist) > 0 else 0.0
        y = float(np.log(post["best"].iloc[:3].mean()) - np.log(g["best"].iloc[0]))
        rows.append(
            {
                "treatment": d,
                "outcome": y,
                "n_from": float(len(src_hist)),
                "log_first_to": float(np.log(g["best"].iloc[0])),
                "n_to_hist": float(len(g)),
            }
        )
        if len(rows) >= 600:
            break
    return pd.DataFrame(rows)


def _honest_t_learner_ate(frame: pd.DataFrame, seed: int = 42) -> tuple[float, int]:
    """Cross-fitted T-learner ATE using gradient boosting when available."""
    try:
        from sklearn.ensemble import GradientBoostingRegressor as _Reg
    except Exception:  # pragma: no cover - sklearn is a core dependency
        from sklearn.tree import DecisionTreeRegressor as _Reg  # type: ignore

    feats = ["n_from", "log_first_to", "n_to_hist"]
    x = frame[feats].to_numpy(dtype=float)
    d = frame["treatment"].to_numpy(dtype=float)
    y = frame["outcome"].to_numpy(dtype=float)
    treated = d == 1
    control = d == 0
    if treated.sum() < 3 or control.sum() < 3:
        return float("nan"), int(len(frame))

    rng = np.random.default_rng(seed)
    order = rng.permutation(len(frame))
    half = len(frame) // 2
    fold_a, fold_b = order[:half], order[half:]
    ate_parts = []
    for fit_idx, eval_idx in ((fold_a, fold_b), (fold_b, fold_a)):
        if len(fit_idx) < 4:
            continue
        fit_treated = fit_idx[d[fit_idx] == 1]
        fit_control = fit_idx[d[fit_idx] == 0]
        if len(fit_treated) < 2 or len(fit_control) < 2:
            continue
        m1 = _Reg(random_state=seed).fit(x[fit_treated], y[fit_treated])
        m0 = _Reg(random_state=seed).fit(x[fit_control], y[fit_control])
        if len(eval_idx) == 0:
            continue
        ate_parts.append(float(np.mean(m1.predict(x[eval_idx]) - m0.predict(x[eval_idx]))))
    if not ate_parts:
        return float("nan"), int(len(frame))
    return float(np.mean(ate_parts)), int(len(frame))


def _econml_import_error() -> str | None:
    """Return a reason string when econml is unavailable, else ``None``."""
    try:
        import econml.dml  # noqa: F401
        from sklearn.ensemble import RandomForestRegressor  # noqa: F401
    except Exception as exc:
        return f"econml unavailable: {type(exc).__name__}: {exc}"
    return None


def _econml_ate(frame: pd.DataFrame) -> tuple[tuple[float, int] | None, str | None]:
    """Optional econml CausalForestDML path.

    Returns ``((ate, n), None)`` on success and ``(None, reason)`` when the fit
    is unavailable or fails, so the caller can record the fallback explicitly.
    """
    try:
        from econml.dml import CausalForestDML
        from sklearn.ensemble import RandomForestRegressor

        feats = ["n_from", "log_first_to", "n_to_hist"]
        x = frame[feats].to_numpy(dtype=float)
        w = frame["treatment"].to_numpy(dtype=float)
        y = frame["outcome"].to_numpy(dtype=float)
        est = CausalForestDML(
            model_y=RandomForestRegressor(n_estimators=60, random_state=42),
            model_t=RandomForestRegressor(n_estimators=60, random_state=42),
            n_estimators=80,
            random_state=42,
        )
        est.fit(y, w, X=x)
        return (float(np.mean(est.effect(x))), int(len(frame))), None
    except Exception as exc:  # noqa: BLE001 - reported via fallback_reason
        return None, f"econml fit failed: {type(exc).__name__}: {exc}"


def causal_forest_transfer_matrix(
    results: pd.DataFrame,
    *,
    min_pairs: int = 12,
    max_persons_per_pair: int = 600,
) -> dict[str, Any]:
    """Estimate transfer effects with a causal forest / honest T-learner.

    Uses ``econml.CausalForestDML`` when installed; otherwise falls back to a
    cross-fitted (honest) T-learner with gradient-boosted base learners. The
    treatment is "any source-event experience before the target-event debut",
    the outcome is the log improvement in the target event after debut.
    """
    df = results.copy()
    if "date" not in df.columns:
        if "start_date" not in df.columns:
            return {"events": [], "matrix": [], "n_pairs": [], "method": "causal_forest"}
        df["date"] = pd.to_datetime(df["start_date"])
    else:
        df["date"] = pd.to_datetime(df["date"])
    df = df[pd.to_numeric(df["best"], errors="coerce") > 0]
    if df.empty:
        return {"events": [], "matrix": [], "n_pairs": [], "method": "causal_forest"}

    df["event_id"] = df["event_id"].astype(str)
    events = sorted(df["event_id"].unique())
    idx = {e: i for i, e in enumerate(events)}
    n = len(events)
    matrix = np.full((n, n), np.nan)
    n_pairs = np.zeros((n, n), dtype=int)

    person_first = df.groupby(["person_id", "event_id"])["date"].min()
    by_event = {e: g.sort_values(["person_id", "date"]) for e, g in df.groupby("event_id")}
    backend = "honest_t_learner"
    econml_error = _econml_import_error()

    for e_from in events:
        src = by_event.get(e_from)
        if src is None:
            continue
        for e_to in events:
            if e_from == e_to:
                matrix[idx[e_from], idx[e_to]] = 0.0
                continue
            dst = by_event.get(e_to)
            if dst is None:
                continue
            frame = _pair_level_frame(dst, src, person_first, e_from)
            if len(frame) < min_pairs:
                n_pairs[idx[e_from], idx[e_to]] = len(frame)
                continue
            used_econml = False
            if econml_error is None:
                econml_result, reason = _econml_ate(frame)
                if econml_result is not None:
                    ate, npair = econml_result
                    used_econml = True
                    backend = "econml_causal_forest"
                else:
                    econml_error = reason
            if not used_econml:
                ate, npair = _honest_t_learner_ate(frame)
            if np.isfinite(ate):
                matrix[idx[e_from], idx[e_to]] = float(ate)
            n_pairs[idx[e_from], idx[e_to]] = npair

    out: dict[str, Any] = {
        "events": events,
        "matrix": matrix.tolist(),
        "n_pairs": n_pairs.tolist(),
        "event_formats": {e: EVENT_FORMATS.get(e, {}).get("format", "time") for e in events},
        "method": backend,
        "note": "Negative ATE suggests target performance improved with source-event experience.",
    }
    if backend != "econml_causal_forest" and econml_error is not None:
        out["fallback"] = "honest_t_learner"
        out["fallback_reason"] = econml_error
    return out
