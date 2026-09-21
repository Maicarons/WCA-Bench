"""Task 2: placement prediction."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.plackett_luce import (
    plackett_luce_scores,
    psych_sheet_predict,
)
from wca_bench.evaluation.metrics import brier_score, kendall_tau, topk_accuracy
from wca_bench.tasks.base import BaseTask
from wca_bench.tasks.result_prediction.task import ResultPredictionTask


class PlacementTask(ResultPredictionTask):
    name = "placement"
    task_type = "ranking"

    def metrics(self) -> list[str]:
        return ["kendall_tau", "top3_overlap", "brier_podium", "n"]

    def baselines(self):
        return [
            Baseline_psych(),
            Baseline_pl(),
        ]

    def _default_metric_fn(self, preds: pd.DataFrame) -> dict[str, Any]:
        if preds.empty:
            return {"n": 0}
        taus = []
        top3s = []
        briers = []
        group_cols = [c for c in ["competition_id", "event_id", "round_type_id"] if c in preds.columns]
        if not group_cols:
            group_cols = ["competition_id"]
        for _, g in preds.groupby(group_cols, dropna=False):
            if len(g) < 2:
                continue
            if "y_true_rank" in g.columns and "y_pred_rank" in g.columns:
                taus.append(kendall_tau(g["y_true_rank"], g["y_pred_rank"]))
            if "y_true" in g.columns and "y_pred_rank" in g.columns:
                top3s.append(topk_accuracy(g["y_true"], g["y_pred_rank"], k=min(3, len(g))))
            if "p_podium" in g.columns:
                y = (g["y_true_rank"] <= 3).astype(float) if "y_true_rank" in g.columns else None
                if y is not None:
                    briers.append(brier_score(y, g["p_podium"]))
        def _mean(xs):
            xs = [x for x in xs if x is not None and np.isfinite(x)]
            return float(np.mean(xs)) if xs else float("nan")

        return {
            "kendall_tau": _mean(taus),
            "top3_overlap": _mean(top3s),
            "brier_podium": _mean(briers),
            "n": int(len(preds)),
        }


class Baseline_psych:
    def __init__(self):
        self.name = "psych_sheet"
        self.kind = "domain"
        self.description = "按历史/预测最佳成绩排序（Psych Sheet 风格）"

    def predict_fn(self, task, **kwargs):
        return psych_sheet_predict(task)


class Baseline_pl:
    def __init__(self):
        self.name = "plackett_luce"
        self.kind = "statistical"
        self.description = "Plackett-Luce utility = -log(历史成绩)"

    def predict_fn(self, task, **kwargs):
        return plackett_luce_scores(task)
