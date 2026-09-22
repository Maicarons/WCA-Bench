"""Stratified evaluation reporting (event / skill / time / continent)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from wca_bench.evaluation.metrics import auc_roc, f1, kendall_tau, mae_log, matthews_corrcoef

DEFAULT_METRICS: dict[str, Callable] = {
    "result_prediction": lambda df: {
        "mae_log": mae_log(df["y_true"], df["y_pred"]),
        "n": int(len(df)),
    },
    "dnf": lambda df: {
        "auc_roc": auc_roc(df["y_true"], df["y_pred"]),
        "f1": f1(df["y_true"], df["y_pred"]),
        "mcc": matthews_corrcoef(df["y_true"], df["y_pred"]),
        "n": int(len(df)),
        "positive_rate": float(df["y_true"].mean()) if len(df) else float("nan"),
    },
    "placement": lambda df: {
        "kendall_tau": kendall_tau(df["y_true_rank"], df["y_pred_rank"])
        if "y_true_rank" in df.columns
        else float("nan"),
        "n": int(len(df)),
    },
}


def stratified_report(
    preds: pd.DataFrame,
    task: str = "result_prediction",
    metric_fn: Callable[[pd.DataFrame], dict] | None = None,
    hard_subset_mask=None,
) -> dict[str, Any]:
    """Compute overall + four-dimensional stratified metrics."""
    fn = metric_fn or DEFAULT_METRICS.get(task)
    if fn is None:
        raise ValueError(f"No metric function for task={task}")

    report: dict[str, Any] = {"overall": fn(preds) if len(preds) else {}, "strata": {}}

    dimensions = {
        "by_event": "event_id",
        "by_skill_level": "skill_level",
        "by_time_slice": "time_slice",
        "by_continent": "continent_id",
        "by_split": "split",
    }
    for name, col in dimensions.items():
        if col not in preds.columns:
            continue
        report["strata"][name] = {
            str(k): fn(g) for k, g in preds.groupby(col, dropna=False) if len(g) > 0
        }

    if hard_subset_mask is not None:
        if callable(hard_subset_mask):
            hard = preds[hard_subset_mask(preds)]
        else:
            hard = preds[pd.Series(hard_subset_mask, index=preds.index).fillna(False)]
        report["hard_subset"] = {"overall": fn(hard) if len(hard) else {}, "n": int(len(hard))}

    if "is_cold_start" in preds.columns:
        cold = preds[preds["is_cold_start"] == True]  # noqa: E712
        warm = preds[preds["is_cold_start"] == False]  # noqa: E712
        report["cold_start"] = {
            "overall": fn(cold) if len(cold) else {},
            "n_cold": int(len(cold)),
            "n_warm": int(len(warm)),
        }

    return report
