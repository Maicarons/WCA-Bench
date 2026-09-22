"""Metric unit tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np
import pytest

from wca_bench.evaluation.metrics import (
    auc_pr,
    auc_roc,
    cliffs_delta,
    cohens_d,
    f1,
    kendall_tau,
    mae,
    mae_log,
    matthews_corrcoef,
    rmse,
)


def test_mae_rmse():
    assert mae([1, 2, 3], [1, 2, 4]) == 1 / 3
    assert abs(rmse([0, 0], [0, 2]) - np.sqrt(2)) < 1e-9


def test_mae_log():
    assert abs(mae_log([100, 200], [100, 200])) < 1e-9
    assert mae_log([100], [200]) > 0


def test_auc_perfect():
    assert auc_roc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert auc_pr([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0


def test_f1_mcc():
    assert f1([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0
    assert matthews_corrcoef([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0


def test_kendall():
    assert kendall_tau([1, 2, 3], [1, 2, 3]) == 1.0
    assert kendall_tau([1, 2, 3], [3, 2, 1]) == -1.0


def test_effect_sizes():
    assert abs(cohens_d([1, 2, 3], [1, 2, 3])) < 1e-9
    assert cliffs_delta([3, 4, 5], [1, 2, 3]) == pytest.approx(8 / 9)
    assert cliffs_delta([10, 11], [1, 2]) == 1.0
