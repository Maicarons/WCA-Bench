"""Split / leakage tests."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd
import pytest

from wca_bench.data.splits import assert_no_leakage, assign_split, freeze_stats, time_slice


def test_assign_split():
    s = assign_split(pd.Series(["2015-01-01", "2023-06-01", "2025-03-01", "1999-01-01"]))
    assert list(s) == ["train", "val", "test", "out_of_window"]


def test_time_slice():
    s = time_slice(pd.Series(["2025-02-01", "2025-08-01", "2026-03-01", "2024-01-01"]))
    assert list(s) == ["test_a", "test_b", "test_c", "val"]


def test_assert_no_leakage_ok():
    assert_no_leakage(pd.Series(["2024-01-01", "2024-06-01"]), date(2025, 1, 1))


def test_assert_no_leakage_raises():
    with pytest.raises(AssertionError):
        assert_no_leakage(pd.Series(["2025-01-02"]), date(2025, 1, 1))


def test_freeze_stats():
    results = pd.DataFrame(
        {
            "person_id": ["P1", "P1", "P2", "P2"],
            "event_id": ["333", "333", "333", "333"],
            "best": [1000, 900, 2000, -1],
            "start_date": ["2020-01-01", "2021-01-01", "2020-02-01", "2025-01-01"],
        }
    )
    stats = freeze_stats(results)
    assert stats["frozen_at"] == "2022-12-31"
    assert ("P1", "333") in stats["person_event_stats"] or "P1::333" in str(stats)
    # 2025 row excluded from train frozen stats
    assert stats["n_train_rows"] == 3
