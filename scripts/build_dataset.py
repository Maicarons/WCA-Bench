#!/usr/bin/env python
"""One-shot dataset build from raw WCA/synthetic export."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wca_bench.data.loader import (  # noqa: E402
    DATA_PROCESSED,
    DATA_RAW,
    DATA_SPLITS,
    build_dataset,
)
from wca_bench.data.synthetic import generate_synthetic_dataset  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["raw", "synthetic"], default="raw")
    parser.add_argument("--raw-dir", type=Path, default=DATA_RAW)
    parser.add_argument("--processed-dir", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--splits-dir", type=Path, default=DATA_SPLITS)
    parser.add_argument("--small", action="store_true")
    args = parser.parse_args(argv)

    if args.source == "synthetic":
        generate_synthetic_dataset(args.raw_dir, small=args.small)

    print(f"Building dataset from {args.raw_dir} ...", flush=True)
    manifest = build_dataset(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        splits_dir=args.splits_dir,
    )
    print(json.dumps(manifest.get("reconciliation", {}), indent=2))
    print(json.dumps({k: v for k, v in manifest.items() if k != "tables"}, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
