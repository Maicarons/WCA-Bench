"""Unit tests for device resolution and the Report.cost compute fields."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd

from wca_bench.tasks.base import Baseline, BaseTask
from wca_bench.utils.device import device_label, resolve_device


def _cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def test_resolve_device_defaults_to_cpu():
    assert resolve_device("cpu") == "cpu"
    assert resolve_device(None) == "cpu"
    assert resolve_device("auto") in {"cpu", "cuda"}


def test_resolve_device_cuda_degrades_without_gpu():
    resolved = resolve_device("cuda")
    if _cuda_available():
        assert resolved == "cuda"
    else:
        assert resolved == "cpu"


def test_device_label_cpu():
    assert device_label("cpu") == "cpu"


class _DummyTask(BaseTask):
    name = "dummy"

    def __init__(self, device: str = "cpu"):
        self.device = device


def test_baseline_cost_cpu_fields():
    task = _DummyTask("cpu")
    baseline = Baseline("m", "method", lambda t: None)
    preds = pd.DataFrame({"x": [1, 2, 3]})

    cost = task.baseline_cost(baseline, preds, "small", 2.0)

    assert cost["mode"] == "small"
    assert cost["baseline_kind"] == "method"
    assert cost["device"] == "cpu"
    assert cost["wall_clock_sec"] == 2.0
    assert abs(cost["cpu_hours"] - 2.0 / 3600.0) < 1e-12
    assert "gpu_hours" not in cost


def test_baseline_cost_ignores_task_device_without_attrs():
    # a baseline that does not touch an accelerator must be reported as CPU even
    # when the task-level requested device is cuda
    task = _DummyTask("cuda")
    baseline = Baseline("plain", "domain", lambda t: None)
    preds = pd.DataFrame({"x": [1]})

    cost = task.baseline_cost(baseline, preds, "small", 1.0)

    assert cost["device"] == "cpu"
    assert "gpu_hours" not in cost


def test_baseline_cost_gpu_fields_when_available():
    task = _DummyTask("cuda")
    baseline = Baseline("m", "method", lambda t: None)
    preds = pd.DataFrame({"x": [1]})
    preds.attrs["device"] = "cuda"

    cost = task.baseline_cost(baseline, preds, "full", 1.0)
    if _cuda_available():
        assert cost["device"].startswith("cuda")
        assert "gpu_hours" in cost
        assert "gpu_model" in cost
    else:
        assert cost["device"] == "cpu"
        assert "gpu_hours" not in cost
