"""Task 3: DNF prediction."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.dnf_rate import historical_dnf_predict
from wca_bench.baselines.tree.logistic_dnf import logistic_dnf_predict
from wca_bench.data.features import build_competition_features, build_result_features
from wca_bench.data.schema import DNF, FORMATS
from wca_bench.evaluation.metrics import (
    auc_pr,
    auc_roc,
    calibration_error,
    f1,
    matthews_corrcoef,
)
from wca_bench.tasks.base import Baseline, BaseTask


class DNFTask(BaseTask):
    name = "dnf"
    task_type = "classification"

    def metrics(self) -> list[str]:
        return ["auc_roc", "auc_pr", "f1", "mcc", "calibration", "n", "positive_rate"]

    def featurize(self, as_of=None):
        df = self.data.results
        test = df[df["split"] == "test"] if len(df) else df
        if test.empty:
            self._features = pd.DataFrame()
            self._train_features = pd.DataFrame()
            return self._features
        if as_of is None:
            dates = pd.to_datetime(
                test["start_date"] if "start_date" in test.columns else test["date"]
            )
            as_of = dates.max().date()
        feats = build_result_features(test, self.data.frozen_stats, as_of=as_of)
        feats = build_competition_features(feats, self.data.frozen_stats)

        att = self.data.result_attempts
        if len(att) and "result_id" in att.columns:
            # sample attempts if extremely large
            if len(att) > 2_000_000:
                # only keep attempts that intersect current feats
                att = att[att["result_id"].isin(set(feats["result_id"].astype(att["result_id"].dtype)))]
            dnf_flags = (
                att.assign(is_dnf=att["value"] == DNF)
                .groupby("result_id")["is_dnf"]
                .any()
                .rename("target_dnf_any")
            )
            feats = feats.merge(dnf_flags, left_on="result_id", right_index=True, how="left")
            feats["target_dnf"] = feats["target_dnf_any"].fillna(feats["best"] == DNF).astype(int)
        else:
            feats["target_dnf"] = (feats.get("best") == DNF).astype(int)

        if "time_slice" not in feats.columns and len(feats):
            feats["time_slice"] = time_slice(feats["date"]).values
        self._features = feats

        train = df[df["split"] == "train"] if len(df) else df
        if len(train) > 80_000:
            train = train.sample(n=80_000, random_state=42)
        if len(train):
            train_as_of = pd.to_datetime(
                train["start_date"] if "start_date" in train.columns else train["date"]
            ).max().date()
            self._train_features = build_result_features(
                train, self.data.frozen_stats, as_of=train_as_of
            )
            if len(att) and "result_id" in att.columns:
                dnf_flags = (
                    att[att["result_id"].isin(self._train_features["result_id"])]
                    .assign(is_dnf=lambda x: x["value"] == DNF)
                    .groupby("result_id")["is_dnf"]
                    .any()
                    .rename("target_dnf_any")
                )
                self._train_features = self._train_features.merge(
                    dnf_flags, left_on="result_id", right_index=True, how="left"
                )
                self._train_features["target_dnf"] = (
                    self._train_features["target_dnf_any"]
                    .fillna(self._train_features.get("best") == DNF)
                    .astype(int)
                )
        else:
            self._train_features = pd.DataFrame()
        return self._features

    def baselines(self) -> list[Baseline]:
        return [
            Baseline(
                "historical_dnf_rate",
                "domain",
                historical_dnf_predict,
                description="选手历史 DNF 率",
            ),
            Baseline(
                "logistic",
                "method",
                logistic_dnf_predict,
                description="Logistic 回归（上下文特征）",
            ),
        ]

    def _default_metric_fn(self, preds: pd.DataFrame) -> dict[str, Any]:
        if preds.empty or "y_true" not in preds.columns:
            return {"n": 0}
        yt = preds["y_true"].fillna(0).to_numpy(dtype=float)
        yp = preds["y_pred"].fillna(0).to_numpy(dtype=float)
        return {
            "auc_roc": auc_roc(yt, yp),
            "auc_pr": auc_pr(yt, yp),
            "f1": f1(yt, yp),
            "mcc": matthews_corrcoef(yt, yp),
            "calibration": calibration_error(yt, yp),
            "n": int(len(preds)),
            "positive_rate": float(np.mean(yt)) if len(yt) else float("nan"),
        }

    def hard_mask(self, preds: pd.DataFrame):
        if "hard_uncertain" in preds.columns:
            return preds["hard_uncertain"].fillna(False).astype(bool)
        if "historical_dnf_rate" in preds.columns:
            r = preds["historical_dnf_rate"]
            return (r >= 0.1) & (r <= 0.3)
        return pd.Series(False, index=preds.index)

    def run_all_baselines(self, mode: str = "small"):
        if not hasattr(self, "_features") or self._features is None:
            self.featurize()
        reports = []
        from wca_bench.tasks.base import Report

        for b in self.baselines():
            try:
                preds = b.predict_fn(self)
                if preds is None or not isinstance(preds, pd.DataFrame):
                    raise TypeError(f"baseline {b.name} returned invalid predictions")
                self._pred_cache[b.name] = preds
                try:
                    hard = self.hard_mask(preds)
                except Exception:
                    hard = None
                rep = self.evaluate(b.name, preds, hard_subset_mask=hard)
                rep.cost = {"mode": mode, "baseline_kind": b.kind}
                reports.append(rep)
            except Exception as exc:
                reports.append(
                    Report(self.name, b.name, overall={"error": str(exc)}, extras={"failed": True})
                )
        return reports
