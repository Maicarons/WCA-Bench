"""Task 4: human-limit estimation from world-record series."""

from __future__ import annotations

import time
from collections.abc import Callable, Hashable
from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.bayesian.hierarchical_limit import hierarchical_limit_estimate
from wca_bench.baselines.statistical.gp_evt_limit import gp_evt_limit_estimate
from wca_bench.baselines.statistical.world_record import (
    build_world_record_series,
    changepoint_limit_estimate,
    exponential_limit_estimate,
)
from wca_bench.data.splits import TRAIN_END as _TRAIN_END
from wca_bench.tasks.base import Baseline, BaseTask, Report


def _predict_limit(task, estimator: Callable[..., dict]) -> pd.DataFrame:
    """Apply a per-event estimator to the train-window WR series."""
    rows = []
    for eid, series in task._series.items():
        s = series
        if len(s):
            s = s.copy()
            s["date"] = pd.to_datetime(s["date"]).dt.date
            s = s[s["date"] <= _TRAIN_END]
        est = estimator(s if len(s) else series)
        est["event_id"] = eid
        rows.append(est)
    return pd.DataFrame(rows)


class HumanLimitTask(BaseTask):
    name = "limit"
    task_type = "extreme"
    significance_metric = "mean_loo_std"
    significance_higher_is_better = False
    significance_unit = "event"

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self._series = build_world_record_series(data.results)
        self._features = pd.DataFrame()

    def metrics(self) -> list[str]:
        return ["limit", "year_converge", "loo_std", "n_points"]

    def featurize(self, as_of=None):
        return self._series

    def baselines(self) -> list[Baseline]:
        return [
            Baseline(
                "exponential_decay",
                "statistical",
                lambda task, **kw: _predict_limit(task, exponential_limit_estimate),
                description="指数衰减趋近极限 + 留一稳定性",
            ),
            Baseline(
                "changepoint",
                "method",
                lambda task, **kw: _predict_limit(task, changepoint_limit_estimate),
                description="后半段斜率外推的变点启发式",
            ),
            Baseline(
                "hierarchical_shrinkage",
                "method",
                hierarchical_limit_estimate,
                description="跨项目经验贝叶斯收缩的极限估计",
            ),
            Baseline(
                "gp_evt",
                "method",
                gp_evt_limit_estimate,
                description="GP 趋势外推 + 极值尾部分位",
            ),
        ]

    def _default_metric_fn(self, preds: pd.DataFrame) -> dict[str, Any]:
        return {}

    def evaluate_limit(self, model_name: str, estimates: pd.DataFrame) -> Report:
        overall = {
            "events": estimates.to_dict(orient="records") if len(estimates) else [],
            "n_events": int(len(estimates)),
            "mean_loo_std": float(estimates["loo_std"].mean())
            if len(estimates) and "loo_std" in estimates.columns
            else float("nan"),
        }
        # domain sanity for 333 if present
        row333 = estimates[estimates["event_id"] == "333"] if len(estimates) else pd.DataFrame()
        if len(row333):
            overall["limit_333"] = float(row333["limit"].iloc[0])
            overall["year_333"] = float(row333["year_converge"].iloc[0])
        return Report(self.name, model_name, overall=overall)

    def unit_losses(self, preds: pd.DataFrame) -> dict[Hashable, float]:
        if preds is None or preds.empty or "event_id" not in preds.columns or "loo_std" not in preds.columns:
            return {}
        out: dict[Hashable, float] = {}
        for _, row in preds.iterrows():
            try:
                val = float(row["loo_std"])
            except (TypeError, ValueError):
                continue
            if np.isfinite(val):
                out[str(row["event_id"])] = val
        return out

    def run_all_baselines(self, mode: str = "small"):
        reports = []
        for b in self.baselines():
            started = time.perf_counter()
            try:
                estimates = b.predict_fn(self)
                elapsed = time.perf_counter() - started
                if estimates is None or not isinstance(estimates, pd.DataFrame):
                    raise TypeError(f"baseline {b.name} returned invalid estimates")
                self._pred_cache[b.name] = estimates
                rep = self.evaluate_limit(b.name, estimates)
                rep.cost = self.baseline_cost(b, estimates, mode, elapsed)
                attrs = getattr(estimates, "attrs", None) or {}
                for key, val in attrs.items():
                    if key not in rep.extras:
                        rep.extras[key] = val
                reports.append(rep)
            except Exception as exc:
                reports.append(
                    Report(self.name, b.name, overall={"error": str(exc)}, extras={"failed": True})
                )
        self.attach_significance(reports)
        return reports
