# Compute and Hardware

Whenever the benchmark is presented, one question comes up: **why does inference run on CPU rather than GPU?** This page answers it with the **measured** profile of the reference run, lists the components that actually executed on CUDA, and specifies how compute cost must be reported.

## 1. Short Answer

WCA-Bench is **not GPU-free** — it is **CPU-first, with the GPU used only where it genuinely pays off**.

- The reference run was executed on an **NVIDIA GeForce RTX 4060 Laptop GPU**, with every baseline launched as `--device cuda`.
- **4 of the 21 baselines actually executed on CUDA**: `lstm` (T1), `gnn` (T2), `xgboost_log` (T1) and `xgboost_dnf` (T3).
- The remaining **17 tabular baselines stayed on CPU** — their feature matrices are only 2k–80k rows and their bottleneck is the *per-competition small-batch forward pass plus rule decoding*, which is latency-sensitive rather than throughput-sensitive.
- Device choice is recorded **per baseline** in every report, so the claim above is checkable rather than asserted — see §4.

## 2. The Reference Run

| Item | Value |
| --- | --- |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB |
| Compute capability | 8.9 |
| Driver | 610.88 |
| CUDA | 13.0 |
| PyTorch | 2.13.0+cu130 |
| Mode / seed | `small` / 42 (single run); 42, 43, 44 (multi-seed) |
| Command | `python scripts/run_all_baselines.py --mode small --device cuda` |

The reports themselves record the resolved device, which is what the tables below are drawn from:

- **On CUDA (4):** `lstm`, `gnn`, `xgboost_log`, `xgboost_dnf`
- **On CPU (17):** `history_mean`, `kde`, `ridge_log`, `psych_sheet`, `plackett_luce`, `kde_simulation`, `historical_dnf_rate`, `logistic`, `beta_binomial`, `exponential_decay`, `changepoint`, `gp_evt`, `hierarchical_shrinkage`, `spearman_correlation`, `did_proxy`, `iv_2sls`, `causal_forest`

## 3. Why the Tabular Baselines Stay on CPU

### 3.1 The workload is latency-sensitive, not throughput-sensitive

The rolling-window protocol evaluates competition by competition: for each competition the model may only use the data available at that competition's `as_of` date (see [Evaluation Protocol and Stratification](/evaluation/protocol#_1-evaluation-protocol)). Each forward pass therefore covers a *tiny* batch — a handful of rows up to a few hundred.

The dominant cost is not matrix algebra at all; it is:

- per-competition feature construction,
- small-batch forward passes,
- and **rule decoding** (multi-blind decoding, ao5 trimming, placement reconstruction, DNF bookkeeping).

GPUs win on large matrix-multiply throughput. At this kernel size, launch overhead and host↔device transfers dominate instead, so moving a tabular baseline to the GPU is usually a net loss. The measured wall-clock times bear this out:

| Baseline | Device | `wall_clock_sec` |
| --- | --- | --- |
| `beta_binomial` | cpu | ≈ 0.0024 |
| `gp_evt` | cpu | ≈ 0.026 |
| `psych_sheet` | cpu | ≈ 0.76 |
| `lstm` | cuda | ≈ 31.39 |

Even the most expensive *GPU* baseline is slower in absolute terms than a typical CPU baseline, because it is doing far more work per sample, not because the device is the problem.

### 3.2 The CPU-side cost is dominated by wide causal estimators

The slowest baselines in the run are the CPU causal estimators — `iv_2sls` (≈ 312.8 s), `causal_forest` (≈ 245.2 s) and `did_proxy` (≈ 38.5 s). Their cost comes from the size of the pairwise event × event problem (17 × 17 pairs over 80 000 observations), not from the device. This is precisely the case where batching (§6) helps, and it is orthogonal to the GPU question.

### 3.3 Reproducibility

CPU execution removes an entire class of non-determinism: no cuDNN kernel selection, no device-specific reduction order, no driver-version dependence. That is why **`cpu` remains the default** even though the reference run used CUDA.

## 4. Cost Reporting Specification

Every report carries a `cost` block. Fields:

| Field | Meaning | When present |
| --- | --- | --- |
| `device` | Resolved device, e.g. `cpu` or `cuda:NVIDIA GeForce RTX 4060 Laptop GPU` | always |
| `wall_clock_sec` | End-to-end wall-clock time of the baseline | always |
| `cpu_hours` | The reported span expressed in hours | always |
| `gpu_hours` | Device time consumed | GPU baselines only |
| `gpu_model` | Accelerator model | GPU baselines only |

Real snippets, copied from the committed reports:

`examples/placement__gnn.json`:

```json
"cost": {
  "mode": "small",
  "baseline_kind": "method",
  "device": "cuda:NVIDIA GeForce RTX 4060 Laptop GPU",
  "wall_clock_sec": 1.170491500000935,
  "cpu_hours": 0.00032513652777803754,
  "gpu_hours": 0.00032513652777803754,
  "gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU"
}
```

`examples/result_prediction__lstm.json`:

```json
"cost": {
  "mode": "small",
  "baseline_kind": "method",
  "device": "cuda:NVIDIA GeForce RTX 4060 Laptop GPU",
  "wall_clock_sec": 31.385063900001114,
  "cpu_hours": 0.008718073305555865,
  "gpu_hours": 0.008718073305555865,
  "gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU"
}
```

A CPU baseline reports only the first three fields, for example `examples/placement__psych_sheet.json`:

```json
"cost": {
  "mode": "small",
  "baseline_kind": "domain",
  "device": "cpu",
  "wall_clock_sec": 0.7611801000002743,
  "cpu_hours": 0.00021143891666674285
}
```

> For GPU baselines `cpu_hours` and `gpu_hours` coincide, because the reported span is the wall-clock time of the run attributed to the device that executed it. They are comparability signals, not energy accounting.

This is the **report-level** block. The **submission-level** `cost.json` aggregates the same quantities across training and inference and adds a per-sample latency; see [Reproducibility Requirements · Compute Cost Report](/evaluation/reproducibility#_4-compute-cost-report) and the [leaderboard submission format](/evaluation/reproducibility#_7-leaderboard-submission-format).

Reports must always state performance **and** cost together, so that "100× the compute for a 1% gain" cannot be hidden.

## 5. Components That Can Use a GPU

| Component | Package | GPU path |
| --- | --- | --- |
| LSTM (T1 result prediction) | `baselines/deep/` | torch device selection |
| GNN (T2 placement prediction) | `baselines/graph/` | torch device selection |
| XGBoost (T1 / T3) | `baselines/tree/` | `device="cuda"` on a CUDA-enabled XGBoost build |

The torch-based baselines and the boosting baselines therefore reached the GPU; the statistical, ranking, Bayesian and causal baselines did not.

### 5.1 Selecting a device

`wca_bench.utils.device.resolve_device()` centralises the decision:

| Requested value | Resolved device |
| --- | --- |
| `None` (default) | `WCA_BENCH_DEVICE` if set, otherwise **`cpu`** |
| `"cpu"` | `cpu` |
| `"cuda"` / `"cuda:<idx>"` | that CUDA device, degrading to `cpu` if torch/CUDA is unavailable |
| `"auto"` | `cuda` when CUDA is actually available, otherwise `cpu` |

Two ways to choose:

- **CLI flag** — every runner accepts `--device {auto,cpu,cuda}`, for example `python scripts/run_all_baselines.py --mode small --device cuda`.
- **Environment variable** — `set WCA_BENCH_DEVICE=cuda` (Windows) or `export WCA_BENCH_DEVICE=cuda` (bash) applies when no explicit device is requested.

`device_label()` produces the human-readable label recorded in the report, such as `cuda:NVIDIA GeForce RTX 4060 Laptop GPU` or `cpu`.

**The default is `cpu`**, so a run without flags is portable and reproducible on any machine. Use `--device auto` to opt into CUDA opportunistically, or `--device cuda` to require it.

## 6. When a GPU Is Worth It

A GPU becomes worthwhile when the *aggregate* work grows, not when a single pass grows:

- a full rolling-window sweep over the complete test window, **times several seeds**, **times** the deep / graph / boosting baselines;
- repeated hyper-parameter sweeps of `baselines/deep/`, `baselines/graph/` and `baselines/tree/`.

The multi-seed run is exactly this scenario: `python scripts/run_multi_seed.py --seeds 42 43 44 --mode small --device cuda` produces `examples/multi_seed.md`.

Guidance when you get there:

1. **Batch across competitions that share an `as_of` date.** The protocol forbids using information from a later competition, so the safe way to build a large batch is to group all competitions with the *same* decision date and run them together. Leakage-freedom is preserved — `assert_no_leakage` still applies to the assembled batch — while the accelerator gets the matrix size it needs.
2. **Keep the rolling-window semantics.** Never mix batches with different `as_of` dates, even if it would be faster.
3. **Report the device.** State `device`, `gpu_hours` and `gpu_model`, and say whether the rest of the leaderboard was produced on CPU; mixed-device leaderboards must be flagged.
4. **Do not expect different conclusions from batching.** Device choice affects runtime, not the ranking of methods — that is why `cpu` stays the default and why the published numbers stay comparable.

## 7. Further Reading

- [Reproducibility Requirements · Compute Cost Report](/evaluation/reproducibility#_4-compute-cost-report)
- [Task Suite · Baseline Inventory](/tasks/#_5-baseline-inventory)
- [Task Suite · Observed Results](/tasks/#_5-3-observed-results-seed-42)
- [Task Suite · Multi-Seed Stability](/tasks/#_5-4-multi-seed-stability)
- [Evaluation Protocol and Stratification](/evaluation/protocol#_1-evaluation-protocol)
- [Development Plan · Directory Organization](/plan/structure)
