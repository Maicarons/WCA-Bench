"""Leakage-free rolling-window evaluation protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Iterable

import pandas as pd

from wca_bench.data.features import build_result_features
from wca_bench.data.splits import TRAIN_END


def assert_no_leakage(feature_dates: Iterable, target_date) -> None:
    from wca_bench.data.splits import assert_no_leakage as _impl

    _impl(feature_dates, target_date)


@dataclass
class RollingWindowProtocol:
    """Evaluate model on test competitions in chronological order.

    Frozen statistics are computed once from training-period data and never updated.
    """

    frozen_stats: dict[str, Any]
    results: pd.DataFrame
    model_fn: Callable[[pd.DataFrame, dict], pd.DataFrame]
    report_fn: Callable[[pd.DataFrame], dict]
    max_competitions: int | None = None
    verbose: bool = False
    history: list[dict] = field(default_factory=list)

    def run(self, split: str = "test") -> dict[str, Any]:
        df = self.results.copy()
        if "split" in df.columns:
            df = df[df["split"] == split]
        if df.empty:
            return {"overall": {}, "per_competition": [], "n_competitions": 0}

        if "date" not in df.columns:
            df["date"] = pd.to_datetime(df["start_date"]).dt.date
        comps = (
            df[["competition_id", "date"]]
            .drop_duplicates()
            .sort_values("date")
        )
        if self.max_competitions is not None:
            comps = comps.head(self.max_competitions)

        per_comp = []
        all_preds = []
        for _, comp in comps.iterrows():
            as_of = comp["date"]
            comp_rows = df[df["competition_id"] == comp["competition_id"]].copy()
            # features may use all history strictly before as_of, plus target rows
            feats = build_result_features(
                df,
                self.frozen_stats,
                as_of=as_of,
                check_leakage=True,
            )
            # keep only current competition targets
            feats = feats[feats["competition_id"] == comp["competition_id"]]
            if feats.empty:
                continue
            preds = self.model_fn(feats, self.frozen_stats)
            if preds is None or preds.empty:
                continue
            preds = preds.copy()
            preds["competition_id"] = comp["competition_id"]
            preds["date"] = as_of
            rep = self.report_fn(preds)
            rep["competition_id"] = comp["competition_id"]
            rep["date"] = str(as_of)
            per_comp.append(rep)
            all_preds.append(preds)

        if not all_preds:
            return {"overall": {}, "per_competition": [], "n_competitions": 0}
        merged = pd.concat(all_preds, ignore_index=True)
        overall = self.report_fn(merged)
        return {
            "overall": overall,
            "per_competition": per_comp,
            "n_competitions": len(per_comp),
            "predictions": merged,
        }
