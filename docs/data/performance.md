# Data Performance Benchmark (A1.9)

This page documents the **measured** performance protocol for the columnar
Parquet storage path versus the CSV fallback, supporting acceptance criterion
**A1.9** ("Parquet load performance ≥ 2× better than Pandas/CSV in memory or
time").

## 1. Protocol

The benchmark is implemented in [`scripts/benchmark_parquet.py`](https://github.com/Maicarons/WCA-Bench/blob/main/scripts/benchmark_parquet.py)
and follows a fixed, reproducible procedure:

1. Load the **same** table from Parquet and from CSV.
2. Time the **median wall-clock** load over `N` iterations (the first run is a
   warm-up so page caches and imports do not skew the measurement).
3. Report three dimensions:
   - **On-disk file size** (`Path.stat().st_size`).
   - **Load time** (median seconds).
   - **In-memory DataFrame size** (`DataFrame.memory_usage(deep=True).sum()`).
4. Ratios are reported **CSV ÷ Parquet**; a value `> 1` means Parquet is
   smaller/faster.

> The in-memory figure measures the resident `DataFrame` allocation, which is
> identical for both formats (it is the decoded object), so the meaningful
> comparison is **file size** and **load time**.

## 2. How to run

```bash
# benchmark an existing processed table
python scripts/benchmark_parquet.py --input data/processed/results.parquet

# or benchmark a freshly generated synthetic table (offline, no network)
python scripts/benchmark_parquet.py --source synthetic --iterations 5
```

The script prints a Markdown table:

```text
| Metric | Parquet | CSV | CSV/Parquet |
| --- | --- | --- | --- |
| File size (MB) | 41.220 | 198.640 | 4.82x |
| Load time median (s) | 0.2140 | 0.9020 | 4.21x |
| In-memory size (MB) | 110.300 | 110.300 | 1.00x |
```

## 3. Expected result at scale

At the full WCA scale (~6.9M result rows, ~6.6M attempts):

- **File size:** Parquet is typically **3–5× smaller** than CSV thanks to
  columnar encoding and dictionary/RLE compression.
- **Load time:** Parquet is typically **2–4× faster** because only the required
  columns are decoded and predicate push-down is possible.
- **In-memory size:** identical between the two formats (same decoded object).

A run that shows `CSV ÷ Parquet ≥ 2` on file size **or** load time satisfies
A1.9. Re-run the script on the target machine whenever the storage layer,
Pandas, or PyArrow versions change, and record the output in the QA report.

## 4. Reference machine

Record the machine that produced the numbers so comparisons stay meaningful:

| Field | Example |
| --- | --- |
| CPU | AMD Ryzen 7 5800H |
| RAM | 32 GB |
| OS | Ubuntu 22.04 |
| Python | 3.12 |
| pandas | 2.x |
| pyarrow | 12+ |

Storage-class claims depend on the reference machine; keep the protocol fixed
and re-measure rather than quoting one-off numbers.
