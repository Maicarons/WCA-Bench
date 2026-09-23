"""Task 2: placement prediction."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.graph.gnn_placement import gnn_placement_predict
from wca_bench.baselines.statistical.plackett_luce import (
    kde_simulate_placement,
    plackett_luce_scores,
    psych_sheet_predict,
)
from wca_bench.evaluation.metrics import brier_score, kendall_tau, topk_accuracy
from wca_bench.tasks.base import Baseline, TaskType
from wca_bench.tasks.result_prediction.task import ResultPredictionTask


class PlacementTask(ResultPredictionTask):
    name = "placement"
    task_type: TaskType = "ranking"
    significance_metric = "kendall_tau"
    significance_higher_is_better = True
    significance_unit = "competition_event_round"

    def metrics(self) -> list[str]:
        return ["kendall_tau", "top3_overlap", "brier_podium", "n"]

    def baselines(self) -> list[Baseline]:
        return [
            Baseline(
                "psych_sheet",
                "domain",
                psych_sheet_predict,
                description="按历史/预测最佳成绩排序（Psych Sheet 风格）",
            ),
            Baseline(
                "plackett_luce",
                "statistical",
                plackett_luce_scores,
                description="Plackett-Luce utility = -log(历史成绩)",
            ),
            Baseline(
                "kde_simulation",
                "statistical",
                kde_simulate_placement,
                description="按预测均值+方差的 Monte-Carlo 排名模拟",
            ),
            Baseline(
                "gnn",
                "method",
                gnn_placement_predict,
                description="选手-比赛异构图 GNN（torch 可选，无 torch 回退 numpy 图传播）",
            ),
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

    def unit_losses(self, preds: pd.DataFrame) -> dict[Hashable, float]:
        gcols = [c for c in ["competition_id", "event_id", "round_type_id"] if c in preds.columns]
        if not gcols or "y_true_rank" not in preds.columns or "y_pred_rank" not in preds.columns:
            return {}
        out: dict[Hashable, float] = {}
        for key, g in preds.groupby(gcols, dropna=False):
            if len(g) < 2:
                continue
            tau = kendall_tau(g["y_true_rank"], g["y_pred_rank"])
            if np.isfinite(tau):
                out[key if isinstance(key, tuple) else (key,)] = float(-tau)
        return out
