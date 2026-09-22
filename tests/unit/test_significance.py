"""Unit tests for Report.significance serialisation and the paired pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd

from wca_bench.tasks.base import BaseTask, Report


def test_report_to_dict_includes_significance():
    rep = Report("dnf", "logistic", overall={"auc_pr": 0.5})
    payload = rep.to_dict()
    assert "significance" in payload
    assert payload["significance"] == {}
    rep.significance = {"reference": "historical_dnf_rate", "p_value": 0.01}
    assert rep.to_dict()["significance"]["reference"] == "historical_dnf_rate"


class _DummyTask(BaseTask):
    name = "dummy"
    significance_metric = "mae_log"
    significance_higher_is_better = False
    significance_unit = "competition_event_round"

    def __init__(self):
        self._pred_cache = {}

    def unit_losses(self, preds):
        return {i: float(v) for i, v in enumerate(preds["loss"].to_numpy())}


def _preds(loss: float) -> pd.DataFrame:
    return pd.DataFrame({"loss": [loss] * 6, "y_pred": [1.0] * 6})


def test_attach_significance_selects_reference_and_pairs():
    task = _DummyTask()
    task._pred_cache = {"best": _preds(0.1), "mid": _preds(0.2), "bad": _preds(0.9)}
    reports = [
        Report("dummy", "bad", overall={"mae_log": 0.9}),
        Report("dummy", "mid", overall={"mae_log": 0.2}),
        Report("dummy", "best", overall={"mae_log": 0.1}),
    ]

    task.attach_significance(reports)

    by_model = {r.model: r.significance for r in reports}
    assert by_model["best"]["is_reference"] is True
    assert by_model["mid"]["reference"] == "best"
    assert by_model["mid"]["metric"] == "mae_log"
    assert by_model["mid"]["n_pairs"] == 6
    assert by_model["mid"]["effect_size"]["name"] == "cohens_d"
    # mid loss (0.2) is worse than reference (0.1) -> positive mean_diff
    assert by_model["mid"]["mean_diff"] > 0


def test_attach_significance_skips_failed_reports():
    task = _DummyTask()
    task._pred_cache = {"ok": _preds(0.5)}
    reports = [
        Report("dummy", "ok", overall={"mae_log": 0.5}),
        Report("dummy", "broken", overall={"error": "boom"}, extras={"failed": True}),
    ]
    task.attach_significance(reports)
    assert reports[0].significance.get("is_reference") is True
    assert reports[1].significance == {}
