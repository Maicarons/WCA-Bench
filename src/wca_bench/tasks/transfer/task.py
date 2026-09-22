"""Task 5: skill transfer analysis."""

from __future__ import annotations

import time
from collections.abc import Hashable
from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.causal.causal_forest import causal_forest_transfer_matrix
from wca_bench.baselines.causal.did import correlation_transfer_matrix, did_transfer_matrix
from wca_bench.baselines.causal.iv import iv_transfer_matrix
from wca_bench.data.splits import TRAIN_END
from wca_bench.tasks.base import Baseline, BaseTask, Report


def _estimates_frame(out: dict[str, Any]) -> pd.DataFrame:
    """Flatten a transfer estimator output into event-pair rows."""
    events = [str(e) for e in out.get("events", [])]
    matrix = out.get("matrix", [])
    n_pairs = out.get("n_pairs")
    rows = []
    if isinstance(matrix, dict):
        mat = matrix
    else:
        mat = np.asarray(matrix, dtype=float) if len(matrix) else np.zeros((len(events), len(events)))
    for i, e_from in enumerate(events):
        for j, e_to in enumerate(events):
            if i == j:
                continue
            try:
                val = float(mat[i][j]) if not isinstance(mat, dict) else float(mat.get((e_from, e_to), np.nan))
            except (TypeError, ValueError, IndexError, KeyError):
                val = float("nan")
            npair = 0
            if n_pairs is not None and not isinstance(n_pairs, dict):
                try:
                    npair = int(np.asarray(n_pairs)[i][j])
                except (TypeError, ValueError, IndexError):
                    npair = 0
            elif isinstance(n_pairs, dict):
                try:
                    npair = int(n_pairs.get((e_from, e_to), 0))
                except (TypeError, ValueError):
                    npair = 0
            identified = bool(np.isfinite(val) and (npair > 0 or n_pairs is None))
            rows.append(
                {
                    "event_from": e_from,
                    "event_to": e_to,
                    "estimate": val,
                    "n_pairs": npair,
                    "identified": identified,
                }
            )
    return pd.DataFrame(rows)


class SkillTransferTask(BaseTask):
    name = "transfer"
    task_type = "causal"
    significance_metric = "n_identified_pairs"
    significance_higher_is_better = True
    significance_unit = "event_pair"

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        df = data.results.copy()
        if len(df):
            if "date" not in df.columns:
                df["date"] = pd.to_datetime(df["start_date"]).dt.date
            df = df[df["date"] <= TRAIN_END]
            if len(df) > 80_000:
                df = df.sample(n=80_000, random_state=42)
        self._train_results = df
        self._features = pd.DataFrame()
        self._raw_cache: dict[str, dict[str, Any]] = {}

    def metrics(self) -> list[str]:
        return ["matrix_events", "n_identified_pairs", "method"]

    def featurize(self, as_of=None):
        return self._train_results

    def baselines(self) -> list[Baseline]:
        return [
            Baseline(
                "spearman_correlation",
                "trivial",
                lambda task, **kw: correlation_transfer_matrix(task._train_results),
                description="项目间成绩 Spearman 相关（非因果，仅作参照）",
            ),
            Baseline(
                "did_proxy",
                "method",
                lambda task, **kw: did_transfer_matrix(task._train_results),
                description="双重差分代理：首次参赛后成绩对数变化",
            ),
            Baseline(
                "iv_2sls",
                "method",
                lambda task, **kw: iv_transfer_matrix(task._train_results),
                description="工具变量 2SLS（国家首次举办源项目作为工具）",
            ),
            Baseline(
                "causal_forest",
                "method",
                lambda task, **kw: causal_forest_transfer_matrix(task._train_results),
                description="因果森林 / honest T-learner 迁移效应",
            ),
        ]

    def unit_losses(self, preds: pd.DataFrame) -> dict[Hashable, float]:
        if preds is None or preds.empty:
            return {}
        out: dict[Hashable, float] = {}
        for _, row in preds.iterrows():
            identified = bool(row.get("identified", False))
            out[(str(row["event_from"]), str(row["event_to"]))] = 0.0 if identified else 1.0
        return out

    def evaluate(self, model_name: str, preds=None, **kwargs) -> Report:
        """Build a Report from a transfer estimator output dict."""
        out = preds if isinstance(preds, dict) else self._raw_cache.get(model_name)
        if out is None:
            return Report(self.name, model_name, overall={})
        self._raw_cache[model_name] = out
        events = out.get("events", [])
        matrix = out.get("matrix", [])
        n_pairs = out.get("n_pairs", None)
        frame = _estimates_frame(out)
        self._pred_cache[model_name] = frame
        if n_pairs is not None:
            identified = int(frame["identified"].sum()) if len(frame) else 0
        elif len(matrix):
            try:
                identified = int(np.sum(np.isfinite(np.asarray(matrix, dtype=float))))
            except (TypeError, ValueError):
                identified = int(frame["identified"].sum()) if len(frame) else 0
        else:
            identified = 0
        extras: dict[str, Any] = {"n": int(len(self._train_results))}
        if out.get("fallback"):
            extras["fallback"] = out["fallback"]
        if out.get("fallback_reason"):
            extras["fallback_reason"] = out["fallback_reason"]
        return Report(
            self.name,
            model_name,
            overall={
                "method": out.get("method"),
                "n_events": len(events),
                "events": events,
                "n_identified_pairs": max(identified, 0),
                "matrix": matrix,
                "n_pairs": n_pairs,
                "note": out.get("note", ""),
            },
            extras=extras,
        )

    def run_all_baselines(self, mode: str = "small"):
        reports = []
        for b in self.baselines():
            started = time.perf_counter()
            try:
                out = b.predict_fn(self)
                elapsed = time.perf_counter() - started
                if not isinstance(out, dict):
                    raise TypeError(f"baseline {b.name} returned invalid transfer output")
                rep = self.evaluate(b.name, out)
                rep.cost = self.baseline_cost(b, out, mode, elapsed)
                reports.append(rep)
            except Exception as exc:
                reports.append(
                    Report(self.name, b.name, overall={"error": str(exc)}, extras={"failed": True})
                )
        self.attach_significance(reports)
        return reports
