#!/usr/bin/env python
"""Build leaderboard artifacts from outputs/reports."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wca_bench.leaderboard import write_leaderboard  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", type=Path, default=ROOT / "outputs" / "reports")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "outputs" / "leaderboard")
    args = parser.parse_args(argv)
    paths = write_leaderboard(args.report_dir, args.out_dir)
    print(paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
