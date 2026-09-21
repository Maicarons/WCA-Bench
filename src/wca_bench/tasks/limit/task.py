"""Task 4: human-limit estimation from world-record series."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.world_record import (
    build_world_record_series,
    changepoint_limit_estimate,
    exponential_limit_estimate,
)
from wca_bench.data.splits import TRAIN_END as _TRAIN_END
from wca_bench.tasks.base import BaseTask, Report


class HumanLimitTask(BaseTask):
    name = "limit"
    task_type = "extreme"

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self._series = build_world_record_series(data.results)
        self._features = pd.DataFrame()

    def metrics(self) -> list[str]:
        return ["limit", "year_converge", "loo_std", "n_points"]

    def featurize(self, as_of=None):
        return self._series

    def baselines(self):
        return [
            _ExpBaseline(),
            _ChangeBaseline(),
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

    def run_all_baselines(self, mode: str = "small"):
        reports = []
        for b in self.baselines():
            try:
                estimates = b.predict_fn(self)
                rep = self.evaluate_limit(b.name, estimates)
                rep.cost = {"mode": mode, "baseline_kind": b.kind}
                reports.append(rep)
            except Exception as exc:
                reports.append(
                    Report(self.name, b.name, overall={"error": str(exc)}, extras={"failed": True})
                )
        return reports


class _ExpBaseline:
    name = "exponential_decay"
    kind = "statistical"
    description = "指数衰减趋近极限 + 留一稳定性"

    def predict_fn(self, task, **kwargs) -> pd.DataFrame:
        rows = []
        # train-window WR series only (no future leakage into limit protocol for test WRs)
        for eid, series in task._series.items():
            if len(series):
                s = series.copy()
                s["date"] = pd.to_datetime(s["date"]).dt.date
                s = s[s["date"] <= _TRAIN_END]
            est = exponential_limit_estimate(s if len(s) else series)
            est["event_id"] = eid
            rows.append(est)
        return pd.DataFrame(rows)


class _ChangeBaseline:
    name = "changepoint"
    kind = "method"
    description = "后半段斜率外推的变点启发式"

    def predict_fn(self, task, **kwargs) -> pd.DataFrame:
        rows = []
        for eid, series in task._series.items():
            if len(series):
                s = series.copy()
                s["date"] = pd.to_datetime(s["date"]).dt.date
                s = s[s["date"] <= _TRAIN_END]
            est = changepoint_limit_estimate(s if len(s) else series)
            est["event_id"] = eid
            rows.append(est)
        return pd.DataFrame(rows)
