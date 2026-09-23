"""Reproducibility tests: A1.2 (checksum stability) and A1.4 (average agreement)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd
import pytest

from wca_bench.data.loader import build_dataset
from wca_bench.data.reconciliation import (
    compute_average_agreement,
    verify_checksums,
)
from wca_bench.data.synthetic import generate_synthetic_dataset

REAL_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
AVERAGE_AGREEMENT_THRESHOLD = 0.995


@pytest.fixture
def synthetic_build(tmp_path):
    raw = tmp_path / "raw"
    proc = tmp_path / "proc"
    splits = tmp_path / "splits"
    generate_synthetic_dataset(raw, small=True)
    manifest = build_dataset(raw_dir=raw, processed_dir=proc, splits_dir=splits)
    return raw, proc, splits, manifest


def test_manifest_has_checksums(synthetic_build):
    _, proc, _, manifest = synthetic_build
    assert "checksums" in manifest
    assert manifest["checksums"], "checksums section must not be empty"
    # every recorded checksum must match the file on disk
    verify_checksums(proc, manifest)


def test_checksums_reproducible(synthetic_build, tmp_path):
    raw, _, _, first = synthetic_build
    proc2 = tmp_path / "proc2"
    splits2 = tmp_path / "splits2"
    second = build_dataset(raw_dir=raw, processed_dir=proc2, splits_dir=splits2)
    # identical inputs -> identical content -> identical checksums
    assert second["checksums"] == first["checksums"]


def test_average_agreement_threshold_synthetic(synthetic_build):
    _, proc, _, _ = synthetic_build
    results = pd.read_parquet(proc / "results.parquet")
    attempts = pd.read_parquet(proc / "result_attempts.parquet")
    rep = compute_average_agreement(results, attempts)
    assert rep["n_compared"] > 0
    assert rep["agreement"] >= AVERAGE_AGREEMENT_THRESHOLD


def test_average_agreement_recorded_in_reconciliation(synthetic_build):
    _, proc, _, manifest = synthetic_build
    recon = manifest["reconciliation"]
    assert recon["average_agreement"] >= AVERAGE_AGREEMENT_THRESHOLD
    assert recon["average_agreement_n"] > 0


@pytest.mark.skipif(
    not (REAL_PROCESSED / "results.parquet").exists()
    or not (REAL_PROCESSED / "result_attempts.parquet").exists(),
    reason="real processed data not present",
)
@pytest.mark.skipif(
    sys.platform.startswith("win") and "CI" in __import__("os").environ,
    reason="skip heavy real-data check on Windows CI runners",
)
def test_average_agreement_threshold_real():
    results = pd.read_parquet(REAL_PROCESSED / "results.parquet")
    attempts = pd.read_parquet(REAL_PROCESSED / "result_attempts.parquet")
    rep = compute_average_agreement(results, attempts)
    assert rep["n_compared"] > 0
    assert rep["agreement"] >= AVERAGE_AGREEMENT_THRESHOLD
