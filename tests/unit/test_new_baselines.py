"""Unit tests for the newly added baselines and their fallback paths."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np
import pandas as pd
import pytest

from wca_bench.baselines.bayesian import beta_binomial_dnf_predict, hierarchical_limit_estimate
from wca_bench.baselines.causal import causal_forest_transfer_matrix, iv_transfer_matrix
from wca_bench.baselines.deep import lstm_result as lstm_mod
from wca_bench.baselines.deep import lstm_result_predict
from wca_bench.baselines.graph import gnn_placement as gnn_mod
from wca_bench.baselines.graph import gnn_placement_predict
from wca_bench.baselines.statistical import gp_evt_limit as gp_mod
from wca_bench.baselines.statistical import gp_evt_limit_estimate
from wca_bench.baselines.tree import xgb_dnf_predict
from wca_bench.baselines.tree.xgb_result import xgb_result_predict


class _FakeData:
    def __init__(self, frozen):
        self.frozen_stats = frozen


class _FakeTask:
    def __init__(self, feats, train=None, frozen=None, series=None):
        self._features = feats
        self._train_features = train if train is not None else feats
        self.data = _FakeData(frozen or {})
        if series is not None:
            self._series = series


def _make_feats(n: int = 6) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "result_id": np.arange(n),
            "person_id": [f"P{i % 3}" for i in range(n)],
            "event_id": ["333"] * n,
            "competition_id": ["C1"] * n,
            "round_type_id": ["1"] * n,
            "date": pd.to_datetime(["2025-02-01"] * n),
            "recent_mean": np.linspace(1000, 1100, n),
            "recent_std": np.linspace(10, 20, n),
            "recent_min": np.linspace(990, 1080, n),
            "recent_slope": np.zeros(n),
            "frozen_mean": np.linspace(1005, 1105, n),
            "frozen_std": np.linspace(11, 21, n),
            "frozen_best": np.linspace(985, 1085, n),
            "best": np.linspace(995, 1095, n),
            "average": np.linspace(1000, 1100, n),
            "historical_dnf_rate": np.linspace(0.0, 0.3, n),
            "n_hist_rounds": np.arange(1, n + 1),
            "n_hist_valid": np.arange(1, n + 1),
            "n_competitions_hist": np.arange(1, n + 1),
            "days_since_last": np.full(n, 30),
            "skill_level": ["intermediate"] * n,
            "time_slice": ["test_a"] * n,
            "continent_id": ["EU"] * n,
            "is_cold_start": [False] * n,
            "target_dnf": [0, 1, 0, 0, 1, 0][:n],
        }
    )


FROZEN = {
    "global_dnf_rate": 0.05,
    "person_event_stats": {
        "P0::333": {"mean_best": 1000.0, "std_best": 10.0, "best": 990.0, "dnf_rate": 0.1},
        "P1::333": {"mean_best": 1050.0, "std_best": 12.0, "best": 1030.0, "dnf_rate": 0.2},
    },
}


def test_beta_binomial_probabilities_in_range():
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    out = beta_binomial_dnf_predict(task)
    assert {"y_pred", "y_true"}.issubset(out.columns)
    assert len(out) == len(task._features)
    assert np.all((out["y_pred"] > 0) & (out["y_pred"] < 1))
    assert np.all((out["y_pred"] >= 0.1) == out["hard_uncertain"])


def test_hierarchical_limit_shrinks_across_events():
    series = {
        "333": pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2005-01-01", "2008-01-01", "2012-01-01", "2016-01-01", "2020-01-01"]
                ).date,
                "value": [12.0, 9.0, 7.0, 6.0, 5.0],
            }
        ),
        "222": pd.DataFrame(
            {
                "date": pd.to_datetime(["2010-01-01", "2014-01-01", "2018-01-01"]).date,
                "value": [3.0, 2.0, 1.5],
            }
        ),
    }
    task = _FakeTask(pd.DataFrame(), series=series)
    out = hierarchical_limit_estimate(task, horizon_years=4.0)
    assert set(out["event_id"]) == {"333", "222"}
    assert out["method"].eq("hierarchical_shrinkage").all()
    assert np.isfinite(out.loc[out["event_id"] == "333", "limit"]).all()
    # shrunk limit cannot exceed the last observed value
    for _, row in out.iterrows():
        last = series[row["event_id"]]["value"].iloc[-1]
        if np.isfinite(row["limit"]):
            assert row["limit"] <= last + 1e-9


def test_gp_evt_limit_runs_and_respects_last():
    series = {
        "333": pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2005-01-01", "2008-01-01", "2012-01-01", "2016-01-01", "2020-01-01"]
                ).date,
                "value": [12.0, 9.0, 7.0, 6.0, 5.0],
            }
        )
    }
    task = _FakeTask(pd.DataFrame(), series=series)
    out = gp_evt_limit_estimate(task)
    assert len(out) == 1
    assert out["method"].iloc[0] == "gp_evt"
    if np.isfinite(out["limit"].iloc[0]):
        assert out["limit"].iloc[0] <= 5.0 + 1e-9


def _transfer_frame() -> pd.DataFrame:
    rows = []
    for i in range(10):
        pid = f"P{i}"
        country = "A" if i < 5 else "B"
        # source event history before target debut for half the persons
        if i % 2 == 0:
            rows.append((pid, "333", "2015-01-01", 1000.0 + i, country))
            rows.append((pid, "333", "2016-01-01", 950.0 + i, country))
        rows.append((pid, "222", "2018-01-01", 500.0 + i, country))
        rows.append((pid, "222", "2019-01-01", 480.0 + i, country))
        rows.append((pid, "222", "2020-01-01", 460.0 + i, country))
    df = pd.DataFrame(rows, columns=["person_id", "event_id", "date", "best", "country_id"])
    df["date"] = pd.to_datetime(df["date"])
    return df


@pytest.mark.parametrize(
    "estimator",
    [iv_transfer_matrix, causal_forest_transfer_matrix],
)
def test_transfer_matrix_shape_and_domain(estimator):
    out = estimator(_transfer_frame(), min_pairs=2)
    events = out["events"]
    assert events == ["222", "333"]
    matrix = np.asarray(out["matrix"], dtype=float)
    assert matrix.shape == (2, 2)
    assert np.allclose(np.diag(matrix), 0.0)
    finite = matrix[np.isfinite(matrix)]
    assert np.all(finite > -10) and np.all(finite < 10)


def test_lstm_fallback_marks_no_torch(monkeypatch):
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    # torch available but the sequence path declined to engage (e.g. <32 windows)
    monkeypatch.setattr(lstm_mod, "_torch_predict", lambda *a, **k: None)
    out = lstm_result_predict(task)
    assert out.attrs.get("fallback") == "no_torch"
    assert out.attrs.get("backend") == "sliding_window_ridge"
    assert np.isfinite(pd.to_numeric(out["y_pred"], errors="coerce")).all()


def test_lstm_torch_error_is_recorded(monkeypatch):
    task = _FakeTask(_make_feats(), frozen=FROZEN)

    def _boom(*args, **kwargs):
        raise RuntimeError("cuda oom in test")

    monkeypatch.setattr(lstm_mod, "_torch_predict", _boom)
    out = lstm_result_predict(task)
    assert out.attrs.get("fallback") == "torch_error"
    assert "RuntimeError: cuda oom in test" in out.attrs.get("torch_error", "")
    assert out.attrs.get("backend") == "sliding_window_ridge"


def test_gnn_fallback_marks_no_torch(monkeypatch):
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    monkeypatch.setattr(gnn_mod, "_torch_graph_adjust", lambda *a, **k: None)
    out = gnn_placement_predict(task)
    assert out.attrs.get("fallback") == "no_torch"
    assert out.attrs.get("backend") == "numpy_graph_propagation"
    assert {"y_pred", "y_pred_rank"}.issubset(out.columns)


def test_gnn_torch_error_is_recorded(monkeypatch):
    task = _FakeTask(_make_feats(), frozen=FROZEN)

    def _boom(*args, **kwargs):
        raise ValueError("bad graph in test")

    monkeypatch.setattr(gnn_mod, "_torch_graph_adjust", _boom)
    out = gnn_placement_predict(task)
    assert out.attrs.get("fallback") == "torch_error"
    assert "ValueError: bad graph in test" in out.attrs.get("torch_error", "")


def test_gnn_covariates_zero_fill_missing_columns():
    df = pd.DataFrame({"recent_mean": [1.0, 2.0], "person_id": ["P1", "P2"]})
    cov = gnn_mod._covariates(df)
    assert cov.shape == (2, 4)
    assert np.isfinite(cov).all()
    # missing columns are zero-filled, present column is carried through
    assert cov[0, 0] == 1.0 and cov[1, 0] == 2.0
    assert np.all(cov[:, 1:] == 0.0)


def test_xgb_result_records_no_xgboost_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, "xgboost", None)
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    out = xgb_result_predict(task)
    assert out.attrs.get("backend") == "random_forest"
    assert out.attrs.get("fallback") == "no_xgboost"
    assert out.attrs.get("device") == "cpu"
    assert "xgboost import failed" in out.attrs.get("fallback_reason", "")
    assert np.isfinite(pd.to_numeric(out["y_pred"], errors="coerce")).all()


def test_xgb_dnf_records_no_xgboost_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, "xgboost", None)
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    out = xgb_dnf_predict(task)
    assert out.attrs.get("dnf_backend") == "random_forest"
    assert out.attrs.get("fallback") == "no_xgboost"
    assert out.attrs.get("device") == "cpu"
    assert "xgboost import failed" in out.attrs.get("fallback_reason", "")


def _cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def test_xgb_passes_cuda_device_to_xgboost(monkeypatch):
    import xgboost

    captured: dict = {}

    class _FakeXGB:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def fit(self, x, y):
            return self

        def predict(self, x):
            return np.zeros(len(x))

    monkeypatch.setattr(xgboost, "XGBRegressor", _FakeXGB)
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    out = xgb_result_predict(task, device="cuda")
    expected = "cuda" if _cuda_available() else "cpu"
    assert captured.get("device") == expected
    assert out.attrs.get("backend") == "xgboost"
    assert out.attrs.get("device", "cpu").startswith(expected)


def test_xgb_dnf_passes_cuda_device_to_xgboost(monkeypatch):
    import xgboost

    captured: dict = {}

    class _FakeXGB:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def fit(self, x, y):
            return self

        def predict_proba(self, x):
            return np.column_stack([np.full(len(x), 0.5), np.full(len(x), 0.5)])

    monkeypatch.setattr(xgboost, "XGBClassifier", _FakeXGB)
    task = _FakeTask(_make_feats(), frozen=FROZEN)
    out = xgb_dnf_predict(task, device="cuda")
    expected = "cuda" if _cuda_available() else "cpu"
    assert captured.get("device") == expected
    assert out.attrs.get("dnf_backend") == "xgboost"


def test_causal_forest_records_econml_fallback():
    out = causal_forest_transfer_matrix(_transfer_frame(), min_pairs=2)
    if out.get("method") != "econml_causal_forest":
        assert out.get("fallback") == "honest_t_learner"
        assert "econml" in out.get("fallback_reason", "")


def test_gp_evt_posterior_reports_jitter():
    t = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 1.0, 2.0])
    mean, std, used_jitter = gp_mod._rbf_gp_posterior(t, y, np.array([3.0]), 1.0, 1e-3)
    assert used_jitter is False
    assert np.isfinite(mean).all() and np.isfinite(std).all()

    # exactly singular kernel (duplicate inputs, no noise) must trigger jitter
    t_dup = np.array([0.0, 1.0, 1.0, 1.0])
    y_dup = np.array([0.0, 1.0, 2.0, 3.0])
    _, _, used_jitter_dup = gp_mod._rbf_gp_posterior(t_dup, y_dup, np.array([2.0]), 1.0, 0.0)
    assert used_jitter_dup is True
