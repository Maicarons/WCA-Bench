"""Task 5: skill transfer analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.causal.did import correlation_transfer_matrix, did_transfer_matrix
from wca_bench.data.splits import TRAIN_END
from wca_bench.tasks.base import BaseTask, Report


class SkillTransferTask(BaseTask):
    name = "transfer"
    task_type = "causal"

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

    def metrics(self) -> list[str]:
        return ["matrix_events", "n_identified_pairs", "method"]

    def featurize(self, as_of=None):
        return self._train_results

    def baselines(self):
        return [_CorrBaseline(), _DidBaseline()]

    def run_all_baselines(self, mode: str = "small"):
        reports = []
        for b in self.baselines():
            try:
                out = b.predict_fn(self)
                events = out.get("events", [])
                matrix = out.get("matrix", [])
                n_pairs = out.get("n_pairs", None)
                identified = 0
                if n_pairs:
                    identified = int(np.sum(np.asarray(n_pairs) > 0)) - len(events)
                elif matrix:
                    identified = int(np.sum(np.isfinite(np.asarray(matrix, dtype=float))))
                rep = Report(
                    self.name,
                    b.name,
                    overall={
                        "method": out.get("method"),
                        "n_events": len(events),
                        "events": events,
                        "n_identified_pairs": max(identified, 0),
                        "matrix": matrix,
                        "n_pairs": n_pairs,
                        "note": out.get("note", ""),
                    },
                    extras={"n": int(len(self._train_results))},
                )
                rep.cost = {"mode": mode, "baseline_kind": b.kind}
                reports.append(rep)
            except Exception as exc:
                reports.append(
                    Report(self.name, b.name, overall={"error": str(exc)}, extras={"failed": True})
                )
        return reports


class _CorrBaseline:
    name = "spearman_correlation"
    kind = "trivial"
    description = "项目间成绩 Spearman 相关（非因果，仅作参照）"

    def predict_fn(self, task, **kwargs):
        return correlation_transfer_matrix(task._train_results)


class _DidBaseline:
    name = "did_proxy"
    kind = "method"
    description = "双重差分代理：首次参赛后成绩对数变化"

    def predict_fn(self, task, **kwargs):
        return did_transfer_matrix(task._train_results)
