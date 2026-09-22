#!/usr/bin/env python
"""Validate a leaderboard submission directory against the WCA-Bench spec.

Checks the required files, the ``report/`` report set and the key/prediction
columns of ``predictions.parquet``. Prints a human-readable PASS/FAIL checklist
and exits non-zero when any check fails.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

REQUIRED_TOP_FILES = [
    "config.yaml",
    "environment.yml",
    "seeds.json",
    "cost.json",
    "README.md",
]

REQUIRED_REPORT_FILES = [
    "overall.json",
    "by_event.json",
    "by_skill_level.json",
    "by_time_slice.json",
    "by_continent.json",
    "calibration.json",
    "significance.json",
    "cost.json",
]

KEY_COLUMNS = ["person_id", "competition_id", "event_id", "round_type_id"]
PREDICTION_COLUMNS = [
    "y_pred",
    "y_pred_rank",
    "p_podium",
    "limit",
    "estimate",
    "y_true",
    "y_true_rank",
]


def _read_predictions(path: Path) -> pd.DataFrame:
    parquet = path / "predictions.parquet"
    if parquet.exists():
        return pd.read_parquet(parquet)
    csv = path / "predictions.csv"
    if csv.exists():
        return pd.read_csv(csv)
    raise FileNotFoundError("predictions.parquet (or predictions.csv) not found")


def validate_submission(submission: str | Path) -> tuple[bool, list[str]]:
    """Return ``(ok, messages)`` for a submission directory."""
    path = Path(submission)
    ok = True
    messages: list[str] = []

    def check(condition: bool, label: str) -> None:
        nonlocal ok
        status = "PASS" if condition else "FAIL"
        if not condition:
            ok = False
        messages.append(f"[{status}] {label}")

    check(path.exists() and path.is_dir(), f"submission directory exists: {path}")
    if not (path.exists() and path.is_dir()):
        return ok, messages

    check((path / "report").is_dir(), "report/ directory present")
    check((path / "predictions.parquet").exists() or (path / "predictions.csv").exists(),
          "predictions.parquet present")

    for name in REQUIRED_TOP_FILES:
        check((path / name).exists(), f"required file present: {name}")

    report_dir = path / "report"
    for name in REQUIRED_REPORT_FILES:
        check((report_dir / name).exists(), f"report/{name} present")

    try:
        preds = _read_predictions(path)
        key_hits = [c for c in KEY_COLUMNS if c in preds.columns]
        pred_hits = [c for c in PREDICTION_COLUMNS if c in preds.columns]
        check(len(key_hits) >= 2, f"key columns present (>=2 of {KEY_COLUMNS}); found {key_hits}")
        check(len(pred_hits) >= 1, f"prediction columns present; found {pred_hits}")
        check(len(preds) > 0, f"predictions non-empty (rows={len(preds)})")
    except Exception as exc:  # noqa: BLE001
        check(False, f"predictions readable: {exc}")

    return ok, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", type=Path, help="path to submission directory")
    args = parser.parse_args(argv)

    ok, messages = validate_submission(args.submission)
    for line in messages:
        print(line)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
