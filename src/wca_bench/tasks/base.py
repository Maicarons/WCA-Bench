"""Unified Task / Baseline / Report abstractions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Protocol, runtime_checkable

import pandas as pd

from wca_bench.data.loader import WCABenchData
from wca_bench.evaluation.stratified import stratified_report

TaskType = Literal["regression", "ranking", "classification", "extreme", "causal"]


@dataclass
class Report:
    task: str
    model: str
    overall: dict[str, Any]
    stratified: dict[str, Any] = field(default_factory=dict)
    hard_subset: dict[str, Any] = field(default_factory=dict)
    cost: dict[str, Any] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "model": self.model,
            "overall": self.overall,
            "stratified": self.stratified,
            "hard_subset": self.hard_subset,
            "cost": self.cost,
            "extras": self.extras,
        }


@dataclass
class Baseline:
    name: str
    kind: str  # trivial | domain | method
    predict_fn: Callable[..., pd.DataFrame]
    fit_fn: Callable[..., Any] | None = None
    description: str = ""
    config: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Task(Protocol):
    name: str
    task_type: TaskType

    def split(self) -> dict[str, pd.DataFrame]: ...
    def featurize(self, as_of) -> pd.DataFrame: ...
    def metrics(self) -> list[str]: ...
    def baselines(self) -> list[Baseline]: ...
    def evaluate(self, model_name: str, preds: pd.DataFrame | None = None) -> Report: ...


class BaseTask:
    """Concrete base implementing shared evaluation bookkeeping."""

    name: str = "base"
    task_type: TaskType = "regression"

    def __init__(self, data: WCABenchData, *, max_test_competitions: int | None = 5):
        self.data = data
        self.max_test_competitions = max_test_competitions
        self._pred_cache: dict[str, pd.DataFrame] = {}

    def split(self) -> dict[str, pd.DataFrame]:
        df = self.data.results
        return {
            "train": df[df["split"] == "train"] if len(df) else df,
            "val": df[df["split"] == "val"] if len(df) else df,
            "test": df[df["split"] == "test"] if len(df) else df,
        }

    def metrics(self) -> list[str]:
        raise NotImplementedError

    def baselines(self) -> list[Baseline]:
        raise NotImplementedError

    def featurize(self, as_of) -> pd.DataFrame:
        raise NotImplementedError

    def _default_metric_fn(self, preds: pd.DataFrame) -> dict[str, Any]:
        raise NotImplementedError

    def evaluate(
        self,
        model_name: str,
        preds: pd.DataFrame | None = None,
        *,
        metric_fn: Callable[[pd.DataFrame], dict] | None = None,
        hard_subset_mask=None,
    ) -> Report:
        if preds is None:
            preds = self._pred_cache.get(model_name)
        if preds is None or preds.empty:
            return Report(self.name, model_name, overall={}, stratified={})
        fn = metric_fn or self._default_metric_fn
        strat = stratified_report(
            preds,
            task=self.name,
            metric_fn=fn,
            hard_subset_mask=hard_subset_mask,
        )
        return Report(
            task=self.name,
            model=model_name,
            overall=strat.get("overall", {}),
            stratified=strat.get("strata", {}),
            hard_subset=strat.get("hard_subset", {}),
            extras={"cold_start": strat.get("cold_start", {}), "n": int(len(preds))},
        )

    def run_baseline(self, baseline: Baseline, **kwargs) -> Report:
        preds = baseline.predict_fn(self, **kwargs)
        self._pred_cache[baseline.name] = preds
        return self.evaluate(baseline.name, preds)

    def run_all_baselines(self, mode: str = "small") -> list[Report]:
        reports = []
        for b in self.baselines():
            try:
                rep = self.run_baseline(b)
                rep.cost = {"mode": mode, "baseline_kind": b.kind}
                reports.append(rep)
            except Exception as exc:  # keep suite resilient
                reports.append(
                    Report(
                        self.name,
                        b.name,
                        overall={"error": str(exc)},
                        extras={"failed": True},
                    )
                )
        return reports
