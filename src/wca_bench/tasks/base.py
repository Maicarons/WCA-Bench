"""Unified Task / Baseline / Report abstractions."""

from __future__ import annotations

import time
from collections.abc import Callable, Hashable
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

import numpy as np
import pandas as pd

from wca_bench.data.loader import WCABenchData
from wca_bench.evaluation.significance import paired_t_test
from wca_bench.evaluation.stratified import stratified_report
from wca_bench.utils.device import device_label, resolve_device

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
    significance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "model": self.model,
            "overall": self.overall,
            "stratified": self.stratified,
            "hard_subset": self.hard_subset,
            "cost": self.cost,
            "extras": self.extras,
            "significance": self.significance,
        }


@dataclass
class Baseline:
    name: str
    kind: str  # trivial | domain | method
    predict_fn: Callable[..., Any]
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
    """Concrete base implementing shared evaluation bookkeeping.

    Subclasses may override ``hard_mask`` and ``unit_losses`` to feed the
    significance pipeline. ``significance_metric`` / ``significance_higher_is_better``
    select the reference baseline (the best model on the task's primary metric),
    while ``unit_losses`` returns per-paired-unit losses (lower is better) used for
    paired t-tests against that reference.
    """

    name: str = "base"
    task_type: TaskType = "regression"
    significance_metric: str | None = None
    significance_higher_is_better: bool = True
    significance_unit: str = "competition_event_round"

    def __init__(self, data: WCABenchData, *, max_test_competitions: int | None = 5):
        self.data = data
        self.max_test_competitions = max_test_competitions
        self._pred_cache: dict[str, Any] = {}

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

    def hard_mask(self, preds: pd.DataFrame):
        """Optional hard-subset selector; return None for the full test set."""
        return None

    def unit_losses(self, preds: pd.DataFrame) -> dict[Hashable, float]:
        """Per-paired-unit loss (lower is better) used for significance tests."""
        return {}

    def _ensure_ready(self) -> None:
        if not hasattr(self, "_features") or self._features is None:
            try:
                self.featurize(None)
            except Exception:
                pass

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

    # ------------------------------------------------------------------ #
    # Significance pipeline
    # ------------------------------------------------------------------ #
    @staticmethod
    def _as_finite(value: Any) -> float | None:
        try:
            out = float(value)
        except Exception:
            return None
        return out if np.isfinite(out) else None

    def _reference_model(self, reports: list[Report]) -> str | None:
        scores: dict[str, float] = {}
        for rep in reports:
            if rep.extras.get("failed"):
                continue
            val = self._as_finite(rep.overall.get(self.significance_metric))
            if val is not None:
                scores[rep.model] = val
        if not scores:
            return None
        if self.significance_higher_is_better:
            return max(scores, key=scores.get)
        return min(scores, key=scores.get)

    def _reference_stub(self, model: str, n_pairs: int) -> dict[str, Any]:
        return {
            "reference": model,
            "metric": self.significance_metric,
            "paired_unit": self.significance_unit,
            "n_pairs": int(n_pairs),
            "mean_diff": 0.0,
            "ci95": [0.0, 0.0],
            "p_value": 1.0,
            "effect_size": {"name": "cohens_d", "value": 0.0},
            "test": "paired_t",
            "seed": 42,
            "is_reference": True,
        }

    def attach_significance(self, reports: list[Report]) -> None:
        """Attach paired significance vs the reference baseline to each report."""
        if not self.significance_metric:
            return
        reference = self._reference_model(reports)
        if reference is None:
            return
        losses: dict[str, dict[Hashable, float]] = {}
        for rep in reports:
            preds = self._pred_cache.get(rep.model)
            if preds is None or not isinstance(preds, pd.DataFrame) or preds.empty:
                continue
            try:
                losses[rep.model] = self.unit_losses(preds)
            except Exception:
                losses[rep.model] = {}
        ref_losses = losses.get(reference, {})
        for rep in reports:
            if rep.extras.get("failed"):
                continue
            if rep.model == reference:
                rep.significance = self._reference_stub(reference, len(ref_losses))
                continue
            cur = losses.get(rep.model, {})
            common = sorted(set(ref_losses) & set(cur), key=str)
            a = [cur[k] for k in common]
            b = [ref_losses[k] for k in common]
            if len(common) < 2:
                rep.significance = {
                    "reference": reference,
                    "metric": self.significance_metric,
                    "paired_unit": self.significance_unit,
                    "n_pairs": int(len(common)),
                    "note": "insufficient paired units",
                }
                continue
            res = paired_t_test(
                a,
                b,
                comparison=f"{rep.model} vs {reference}",
                task=self.name,
                metric=self.significance_metric,
                paired_unit=self.significance_unit,
            )
            res["reference"] = reference
            res.pop("comparison", None)
            res.pop("task", None)
            rep.significance = res

    def baseline_cost(
        self,
        baseline: Baseline,
        preds: Any,
        mode: str,
        elapsed_sec: float,
    ) -> dict[str, Any]:
        """Build the compute-cost record for the report.

        Always includes ``mode`` / ``baseline_kind`` / ``device`` /
        ``wall_clock_sec`` / ``cpu_hours``; GPU fields are added only when the
        baseline actually ran on CUDA.
        """
        attrs = getattr(preds, "attrs", None) or {}
        # Only baselines that actually touch an accelerator declare ``device`` in
        # their prediction attrs; everything else is CPU by definition.
        requested = attrs.get("device", "cpu")
        device = resolve_device(requested)
        label = device_label(device)
        elapsed = float(elapsed_sec)
        cost: dict[str, Any] = {
            "mode": mode,
            "baseline_kind": baseline.kind,
            "device": label,
            "wall_clock_sec": elapsed,
            "cpu_hours": elapsed / 3600.0,
        }
        if label.startswith("cuda"):
            cost["gpu_hours"] = elapsed / 3600.0
            cost["gpu_model"] = attrs.get("gpu_model", label.split(":", 1)[-1])
        return cost

    def run_all_baselines(self, mode: str = "small") -> list[Report]:
        self._ensure_ready()
        reports: list[Report] = []
        for b in self.baselines():
            started = time.perf_counter()
            try:
                preds = b.predict_fn(self)
                elapsed = time.perf_counter() - started
                if preds is None or not isinstance(preds, pd.DataFrame):
                    raise TypeError(f"baseline {b.name} returned invalid predictions")
                self._pred_cache[b.name] = preds
                try:
                    hard = self.hard_mask(preds)
                except Exception:
                    hard = None
                rep = self.evaluate(b.name, preds, hard_subset_mask=hard)
                rep.cost = self.baseline_cost(b, preds, mode, elapsed)
                attrs = getattr(preds, "attrs", None) or {}
                for key, val in attrs.items():
                    if key not in rep.extras:
                        rep.extras[key] = val
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
        self.attach_significance(reports)
        return reports
