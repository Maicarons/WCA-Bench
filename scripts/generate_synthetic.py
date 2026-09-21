#!/usr/bin/env python
"""Generate a synthetic WCA-like export for offline/CI use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wca_bench.data.synthetic import SyntheticConfig, generate_synthetic_dataset  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--persons", type=int, default=400)
    parser.add_argument("--competitions", type=int, default=80)
    args = parser.parse_args(argv)
    cfg = SyntheticConfig(
        n_persons=args.persons,
        n_competitions=args.competitions,
        seed=args.seed,
    )
    paths = generate_synthetic_dataset(args.out, cfg, small=args.small)
    for k, v in paths.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
