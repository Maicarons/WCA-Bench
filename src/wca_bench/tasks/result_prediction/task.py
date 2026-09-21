"""Task 1: result prediction."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.history_mean import history_mean_predict
from wca_bench.baselines.statistical.kde import kde_predict_result
from wca_bench.baselines.tree.ridge_result import ridge_result_predict
from wca_bench.baselines.tree.xgb_result import xgb_result_predict
from wca_bench.data.features import build_competition_features, build_result_features
from wca_bench.data.splits import time_slice
from wca_bench.evaluation.metrics import coverage, mae_log, rmse_log
from wca_bench.tasks.base import Baseline, BaseTask, Report


class ResultPredictionTask(BaseTask):
    name = "result_prediction"
    task_type = "regression"

    def metrics(self) -> list[str]:
        return ["mae_log", "rmse_log", "coverage90", "n"]

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
        if "time_slice" not in feats.columns and len(feats):
            feats["time_slice"] = time_slice(feats["date"]).values
        if "best" not in feats.columns:
            merge_cols = [c for c in ["id", "best", "average"] if c in test.columns]
            feats = feats.merge(
                test[merge_cols].rename(columns={"id": "result_id"}),
                on="result_id",
                how="left",
                suffixes=("", "_raw"),
            )
        self._features = feats

        train = df[df["split"] == "train"] if len(df) else df
        if len(train) > 120_000:
            train = train.sample(n=120_000, random_state=42)
        if len(train):
            train_as_of = pd.to_datetime(
                train["start_date"] if "start_date" in train.columns else train["date"]
            ).max().date()
            self._train_features = build_result_features(
                train, self.data.frozen_stats, as_of=train_as_of
            )
        else:
            self._train_features = pd.DataFrame()
        return self._features

    def baselines(self) -> list[Baseline]:
        return [
            Baseline(
                "history_mean",
                "trivial",
                history_mean_predict,
                description="最近/冻结历史均值",
            ),
            Baseline(
                "kde",
                "statistical",
                kde_predict_result,
                description="高斯 KDE bootstrap 轮次模拟",
            ),
            Baseline(
                "ridge_log",
                "method",
                ridge_result_predict,
                description="Ridge on log(best) with frozen features",
            ),
            Baseline(
                "xgboost_log",
                "method",
                xgb_result_predict,
                description="XGBoost on log(best)",
            ),
        ]

    def _default_metric_fn(self, preds: pd.DataFrame) -> dict[str, Any]:
        y_true = preds["y_true"].to_numpy(dtype=float) if "y_true" in preds.columns else np.array([])
        y_pred = preds["y_pred"].to_numpy(dtype=float) if "y_pred" in preds.columns else np.array([])
        out = {
            "mae_log": mae_log(y_true, y_pred),
            "rmse_log": rmse_log(y_true, y_pred),
            "n": int(np.sum(np.isfinite(y_true) & np.isfinite(y_pred))),
        }
        if "y_lo" in preds.columns and "y_hi" in preds.columns:
            out["coverage90"] = coverage(y_true, preds["y_lo"], preds["y_hi"])
        return out

    def hard_mask(self, preds: pd.DataFrame):
        if "recent_std" in preds.columns and "recent_mean" in preds.columns:
            ratio = preds["recent_std"] / preds["recent_mean"].replace(0, np.nan)
            thr = ratio.quantile(0.75)
            return ratio >= thr
        return pd.Series(False, index=preds.index)

    def run_all_baselines(self, mode: str = "small"):
        if not hasattr(self, "_features") or self._features is None:
            self.featurize()
        reports = []
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
