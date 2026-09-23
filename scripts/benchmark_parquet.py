#!/usr/bin/env python
"""Benchmark Parquet vs CSV read performance (time + memory + disk).

Supports acceptance criterion A1.9: a documented performance benchmark
comparing the columnar Parquet path against the CSV fallback.

Protocol (see docs/data/performance.md):
  1. Load the same table from Parquet and from CSV.
  2. Time median wall-clock load over N iterations (first run is a warm-up).
  3. Report on-disk file size and in-memory DataFrame size
     (``DataFrame.memory_usage(deep=True).sum()``).
  4. Ratios are reported Parquet-vs-CSV; values > 1 mean CSV is slower/larger.

Usage:
  python scripts/benchmark_parquet.py --input data/processed/results.parquet
  python scripts/benchmark_parquet.py --source synthetic --iterations 5
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wca_bench.data.synthetic import generate_synthetic_dataset  # noqa: E402
from wca_bench.utils.io import read_table, save_table  # noqa: E402


def _bench(path: Path, iterations: int) -> tuple[float, int]:
    read_table(path)  # warm-up (page cache, imports)
    times: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        df = read_table(path)
        times.append(time.perf_counter() - t0)
    times.sort()
    median = times[len(times) // 2]
    mem = int(df.memory_usage(deep=True).sum())
    return median, mem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=None,
        help="existing Parquet/CSV table to benchmark (default: synthetic results)",
    )
    parser.add_argument("--source", choices=["synthetic"], default="synthetic")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--tmp", type=Path, default=ROOT / ".bench_tmp")
    args = parser.parse_args(argv)

    tmp = args.tmp
    tmp.mkdir(parents=True, exist_ok=True)

    if args.input:
        pq = Path(args.input)
        if not pq.exists():
            raise FileNotFoundError(pq)
        df = read_table(pq)
    else:
        raw = tmp / "raw"
        proc = tmp / "proc"
        splits = tmp / "splits"
        generate_synthetic_dataset(raw, small=True)
        from wca_bench.data.loader import build_dataset

        build_dataset(raw_dir=raw, processed_dir=proc, splits_dir=splits)
        pq = proc / "results.parquet"
        df = read_table(pq)

    csv = tmp / (pq.stem + ".csv")
    save_table(df, csv)

    pq_time, pq_mem = _bench(pq, args.iterations)
    csv_time, csv_mem = _bench(csv, args.iterations)
    pq_size = pq.stat().st_size
    csv_size = csv.stat().st_size

    ratio_time = csv_time / pq_time if pq_time else float("nan")
    ratio_mem = csv_mem / pq_mem if pq_mem else float("nan")
    ratio_size = csv_size / pq_size if pq_size else float("nan")

    print("| Metric | Parquet | CSV | CSV/Parquet |")
    print("| --- | --- | --- | --- |")
    print(f"| File size (MB) | {pq_size / 1e6:.3f} | {csv_size / 1e6:.3f} | {ratio_size:.2f}x |")
    print(f"| Load time median (s) | {pq_time:.4f} | {csv_time:.4f} | {ratio_time:.2f}x |")
    print(f"| In-memory size (MB) | {pq_mem / 1e6:.3f} | {csv_mem / 1e6:.3f} | {ratio_mem:.2f}x |")
    print()
    print(f"rows={len(df):,}  iterations={args.iterations}")
    print(
        "Interpretation: Parquet should be smaller on disk and faster to load "
        "than CSV at the 6.6M-row scale (ratios > 1 favour Parquet)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
