#!/usr/bin/env python
"""Build leaderboard artifacts from outputs/reports."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wca_bench.leaderboard import write_leaderboard  # noqa: E402


def _is_report(path: Path) -> bool:
    """Only flat reports enter the leaderboard.

    A report is a JSON *object* carrying ``task`` and ``model``. This guard keeps
    derived artifacts out of the staging directory — notably
    ``examples/leaderboard.json``, whose records also expose ``task``/``model``
    (as a JSON array) and would otherwise add unranked junk rows.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return isinstance(payload, dict) and "task" in payload and "model" in payload


def _stage_report_dirs(report_dirs: list[Path]) -> Path:
    """Copy reports from several directories into one temporary directory.

    ``write_leaderboard`` reads a single directory, so community submissions are
    merged with the offline reports here. The caller must clean up the result.
    """
    staging = Path(tempfile.mkdtemp(prefix="wca-reports-"))
    staged = 0
    for directory in report_dirs:
        if not directory.is_dir():
            print(f"[warn] report directory missing, skipped: {directory}")
            continue
        for path in sorted(directory.glob("*.json")):
            if path.name.startswith("_") or not _is_report(path):
                continue
            shutil.copy2(path, staging / path.name)
            staged += 1
    print(f"[info] staged {staged} report(s) from {len(report_dirs)} director(ies).")
    return staging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report-dir",
        type=Path,
        action="append",
        default=None,
        help="Directory holding report JSONs; repeat to merge several directories.",
    )
    parser.add_argument(
        "--community-dir",
        type=Path,
        default=ROOT / "community-submissions",
        help="Directory holding community submissions.",
    )
    parser.add_argument(
        "--with-community",
        dest="with_community",
        action="store_true",
        help="Merge community submissions into the leaderboard.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "outputs" / "leaderboard",
        help="Where leaderboard.csv/json/md are written.",
    )
    args = parser.parse_args(argv)

    report_dirs: list[Path] = args.report_dir or [ROOT / "outputs" / "reports"]
    if args.with_community:
        report_dirs = [*report_dirs, args.community_dir]

    source = report_dirs[0]
    staging: Path | None = None
    if len(report_dirs) > 1:
        staging = _stage_report_dirs(report_dirs)
        source = staging

    try:
        paths = write_leaderboard(source, args.out_dir)
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)

    print(paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
