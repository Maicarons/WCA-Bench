# Reproducibility Requirements

## 1. Submission Checklist

Every submitted model **must** provide:

- [ ] Complete **training code** and **random seeds**
- [ ] **Data preprocessing scripts** (or a reference to the benchmark pipeline version)
- [ ] A HuggingFace hosting link for the **model weights**
- [ ] A **report of the inference-time compute cost** (GPU hours or CPU hours)

## 2. Environment and Versions

| Item | Requirement |
| --- | --- |
| Python version | Pinned in `pyproject.toml` / `environment.yml` |
| Dependency versions | Locked (lockfile or exact version numbers) |
| Data snapshot | Record the WCA export snapshot version (e.g. v2.0.2) |
| Hardware | Record GPU / CPU models and counts |
| Randomness | Fix all random sources (Python, NumPy, PyTorch, CUDA) |

## 3. Random Seed Strategy

```python
def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

Requirements:

- Primary results must report the mean ± standard deviation over **at least 3 seeds** — *satisfied*: seeds **42 / 43 / 44**, aggregated by `scripts/run_multi_seed.py --device cuda` into `examples/multi_seed.md`
- The list of seeds used must be given explicitly in the report
- The seeds of bootstrap / Monte Carlo simulations must also be fixed

The multi-seed artifact covers all 21 baselines across the five tasks and is committed as `examples/multi_seed.md` (machine-readable output: `outputs/multi_seed/multi_seed.json`). Because seeds change which competitions are sampled from the test window, the reported spread measures the **sampling variance of the evaluation window**, not training instability; T4 (a deterministic estimator over a fixed world-record series) and T5 (computed from the full training history) are correspondingly stable. Headline numbers are tabulated in [Task Suite · Multi-Seed Stability](/tasks/#_5-4-multi-seed-stability).

## 4. Compute Cost Report

```json
{
  "task": "result_prediction",
  "training": {"hardware": "A100-40G", "gpu_hours": 12.5, "wall_clock_hours": 2.1},
  "inference": {"hardware": "A100-40G", "gpu_hours": 0.3, "per_sample_ms": 4.2},
  "total": {"gpu_hours": 12.8}
}
```

When comparing against baselines, the **performance–cost trade-off** must also be given, so that cases such as "100× the compute for a 1% gain" cannot be hidden.

Reports record the resolved `device`, the wall-clock time and the CPU hours; a GPU run additionally records `gpu_hours` and the accelerator model. The rationale for the CPU-first default, the full field list, and guidance on when a GPU is worth using are given in [Compute and Hardware](/evaluation/compute); the field-level specification is in [Compute and Hardware · Cost Reporting Specification](/evaluation/compute#_4-cost-reporting-specification).

## 5. Artifacts and Verification

| Artifact | Verification method |
| --- | --- |
| Preprocessed Parquet | Record row counts, column names, and checksums (SHA256) |
| Split indices | Reconcile with raw table row counts |
| Model weights | Record file checksums and training configuration |
| Predictions | Save the raw predictions for every competition so metrics can be recomputed |

## 6. Reproduction Levels

| Level | Definition |
| --- | --- |
| L1 Rerunnable | Code runs, scripts complete |
| L2 Reproducible | L1 + results agree within tolerance (±1% on metrics) |
| L3 Verifiable | L2 + raw predictions downloadable, metrics independently recomputable |

**The minimum requirement for benchmark inclusion is L2; the main leaderboard requires L3.**

## 7. Leaderboard Submission Format

```text
submission/
├── report/               # See the report template in the Evaluation Framework
├── predictions.parquet   # Raw predictions for every competition
├── config.yaml           # Model and training configuration
├── environment.yml       # Environment lock
├── seeds.json            # Random seeds
├── cost.json             # Compute report
└── README.md             # Reproduction steps
```

Community entries carry the same information in a single flat report JSON
(`{task}__{model}.json`) added under `community-submissions/`. The accepted
schema and the validation command are documented in
[community-submissions/README.md](https://github.com/Maicarons/WCA-Bench/blob/main/community-submissions/README.md),
and the full workflow — including how to submit through the leaderboard Space —
is described in [Join the Leaderboard](/guide/participate).

## 8. Further Reading

- [Evaluation Framework · Overview →](/evaluation/)
- [Development Plan · Acceptance Criteria →](/plan/acceptance)
