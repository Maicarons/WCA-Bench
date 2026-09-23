# Data Infrastructure · Overview

Data is the foundation of WCA-Bench. This chapter describes the data sources, the preprocessing pipeline, and the splitting strategy; together these three determine the scientific credibility of the benchmark.

## 1. Chapter Structure

| Chapter | Contents |
| --- | --- |
| [Data Sources and Table Schemas](/data/sources) | Core tables, scale, and fields of the official WCA export |
| [Preprocessing Pipeline](/data/pipeline) | Result decoding, scramble handling, round normalization, leakage protection |
| [Data Splitting Strategy](/data/splits) | Temporal splitting, competitor longitudinal sequences, extended test set |
| [Performance Benchmark](/data/performance) | Parquet-vs-CSV protocol and measured load/memory ratios (A1.9) |

## 2. Design Principles

1. **Public data only.** All data comes from the official public WCA database export; no self-built collection.
2. **Columnar first.** At the 6.6M-row scale, Polars + Parquet is the inevitable choice for both performance and cost.
3. **Explicit rule modeling.** DNF/DNS encodings, multi-blind formats, and the trimming mechanism must be handled explicitly during preprocessing, not left for the model to "guess".
4. **Leakage protection built in.** Temporal splitting and frozen benchmark statistics are first-class citizens of the pipeline, not after-the-fact patches.
5. **Reproducible.** The pipeline runs with a single command, its artifacts are verifiable, and all randomness can be fixed.

## 3. Data Flow

```text
data/raw/*.tsv
    │
    │  decode (results / multi-blind / special values)
    ▼
data/processed/*.parquet  ──►  features cache
    │
    │  split (temporal splitting)
    ▼
data/splits/{train,val,test}.*  ──►  task adapter layer
```

## 4. Key Scale Reference

| Table | Scale (approx.) |
| --- | --- |
| persons | 289k rows |
| competitions | 17.7k rows |
| results | 6.6M rows |
| scrambles | 3.1M rows |
| events | 17 active events + retired events |

## 5. Further Reading

- [Data Sources and Table Schemas →](/data/sources)
- [Preprocessing Pipeline →](/data/pipeline)
- [Data Splitting Strategy →](/data/splits)
