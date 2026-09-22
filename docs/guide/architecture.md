# Technical Approach Overview

This chapter presents the overall technical route of WCA-Bench. Detailed content is covered in [Data Infrastructure](/data/), the [Task Suite](/tasks/), and the [Evaluation Framework](/evaluation/).

## 1. Technical Route Overview

```text
WCA raw export (TSV)
      │
      ▼
┌─────────────────────────┐
│  Preprocessing pipeline │  Result decoding / multi-blind decoding / round normalization
│  loader → decoders      │  Special values (-1 DNF, -2 DNS, 0 no result)
│  → features             │  Temporal leakage protection
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  Columnar storage       │  Parquet + splits (train/val/test)
│  data/processed         │  Per-competitor longitudinal sequence index
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  Five-task adapter      │  T1 regression / T2 ranking / T3 classification
│  src/tasks/*            │  T4 extremes / T5 causal inference
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  Baseline models        │  Statistical / tree / sequence / graph baselines
│  src/baselines/*        │  Bayesian and causal baselines
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  Unified evaluation     │  Rolling-window protocol / four-way stratification / statistical tests
│  src/evaluation/*       │  Bootstrap CI / effect sizes
└─────────────────────────┘
      │
      ▼
   Leaderboard / paper / dataset release
```

## 2. Codebase Structure

```text
wca-bench/
├── data/
│   ├── raw/                    # Raw WCA export files
│   ├── processed/              # Preprocessed Parquet files
│   └── splits/                 # Temporally split train/val/test indices
├── src/
│   ├── data/
│   │   ├── loader.py           # Data loading and preprocessing
│   │   ├── decoders.py         # Multi-blind and result value decoding
│   │   └── features.py         # Feature engineering
│   ├── tasks/
│   │   ├── result_prediction/  # Task 1
│   │   ├── placement/          # Task 2
│   │   ├── dnf/                # Task 3
│   │   ├── limit/              # Task 4
│   │   └── transfer/           # Task 5
│   ├── baselines/              # Baseline model implementations
│   ├── evaluation/             # Evaluation metrics and protocols
│   └── utils/
├── configs/                    # Experiment configuration files
├── notebooks/                  # Exploratory analysis
├── tests/                      # Unit tests
├── docs/                       # Documentation (this VitePress site)
└── scripts/                    # Automation scripts
```

> The complete directory organization and documentation layering design is described in [Development Plan · Directory Organization and Documentation Layering](/plan/structure).

## 3. Core Technical Decisions

### 3.1 Data Layer: Columnar First

| Decision | Approach | Rationale |
| --- | --- | --- |
| Loading engine | Polars instead of Pandas for initial loading | 3–5× better memory efficiency at 6.6M rows |
| Storage format | Parquet (PyArrow) | Columnar reads, supporting column pruning and predicate pushdown |
| Feature cache | Persistent cache for frequently accessed competitor features | Avoids repeated computation |
| Data loader | Provide a streaming loader | Supports large-scale training and memory-constrained environments |

### 3.2 Task Layer: Unified Abstraction

All tasks follow a unified interface contract:

- `Task.split()` — returns the task's temporal split view
- `Task.featurize()` — constructs model inputs from raw records
- `Task.evaluate()` — returns a standard metrics dictionary plus stratified results
- `Task.baseline()` — registers and runs baseline models

This abstraction guarantees that "the same evaluation code evaluates every model", which is the key to the benchmark's credibility.

### 3.3 Evaluation Layer: Leakage-Free First

- **Temporal splitting** rather than random splitting (a basic principle of sports data analysis)
- **Rolling window**: for every competition in the test set, the model may only access data preceding that competition
- **Frozen benchmark statistics**: historical means, world records, etc. are computed on the training period and then frozen
- **Stratified reporting**: event / competitor skill level / time / region

## 4. Core Dependencies

| Area | Dependencies |
| --- | --- |
| Data processing | Pandas, Polars (large-scale data), PyArrow (Parquet) |
| Machine learning | scikit-learn, XGBoost, LightGBM |
| Deep learning | PyTorch, PyTorch Lightning |
| Probabilistic programming | PyMC, NumPyro (Bayesian models) |
| Graph learning | PyTorch Geometric (GNN baselines) |
| Experiment management | Weights & Biases or MLflow |
| Data hosting | HuggingFace Datasets |
| Documentation site | VitePress |

## 5. Key Domain Handling Points

### 5.1 Result Value Decoding

| format | Meaning of the value | Example |
| --- | --- | --- |
| `time` | Hundredths of a second | `8653` → 1:26.53 |
| `number` | Raw number (fewest moves) | `28` → 28 moves |
| `multi` | Multi-blind encoding | `1SSAATTTTT` / `0DDTTTTTMM` |
| Special values | DNF / DNS / no result | `-1` / `-2` / `0` |

### 5.2 Round Format Normalization

- best of 3: take the best attempt
- average of 5 / mean of 3: the average must be computed as the arithmetic mean **after discarding the best and worst attempts**
- A single DNF is amplified by the trimming mechanism in ao5, and must therefore be modeled explicitly

### 5.3 Scramble Sequence Handling

The scrambles for the `333mbf` event consist of multiple newline-separated 3x3 scrambles. In the TSV version, newlines are replaced by the `|` character, so preprocessing must restore and normalize them.

## 6. Related Sections

- [Data Infrastructure · Overview →](/data/)
- [Task Suite · Overview →](/tasks/)
- [Evaluation Framework · Overview →](/evaluation/)
- [Development Plan · Dependencies →](/plan/dependencies)
