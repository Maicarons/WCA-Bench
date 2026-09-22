"""Unit tests for the submission validator (PASS and FAIL branches)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_submission import validate_submission  # noqa: E402

TEMPLATE = Path(__file__).resolve().parents[2] / "examples" / "submission_template"


def test_template_passes():
    ok, messages = validate_submission(TEMPLATE)
    assert ok, messages
    assert any(line.startswith("[PASS]") for line in messages)
    assert not any(line.startswith("[FAIL]") for line in messages)


def test_missing_files_fail():
    ok, messages = validate_submission(TEMPLATE / "does_not_exist")
    assert not ok
    assert any("[FAIL]" in line for line in messages)


def test_incomplete_submission_fails(tmp_path):
    (tmp_path / "report").mkdir()
    (tmp_path / "predictions.parquet").write_bytes(b"not a parquet")
    ok, messages = validate_submission(tmp_path)
    assert not ok
    # missing top-level files and report files must be reported
    assert any("config.yaml" in line and "[FAIL]" in line for line in messages)
    assert any("significance.json" in line and "[FAIL]" in line for line in messages)
