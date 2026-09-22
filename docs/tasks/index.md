# Task Suite · Overview

WCA-Bench contains five core tasks, spanning difficulty levels from **basic prediction** to **advanced inference**.

## 1. Task Matrix

| ID | Task | Learning paradigm | Core metrics | Domain challenge |
| --- | --- | --- | --- | --- |
| [T1](/tasks/result-prediction) | Result Prediction | Regression | MAE / RMSE (log domain) + calibration error | Non-stationarity of performance, variance differences across events |
| [T2](/tasks/placement) | Placement Prediction | Ranking | Kendall's τ, top-3 accuracy, Brier | Competitor interaction effects, trimming mechanism amplifying DNF impact |
| [T3](/tasks/dnf) | DNF Prediction | Imbalanced binary classification | AUC-ROC/PR, F1, MCC | Rare events, extremely uneven across events, sequential dependence |
| [T4](/tasks/limit) | Human Limit Estimation | Extreme value / extrapolation | Stability, interval coverage, domain consistency | Extrapolation risk, vastly different data density |
| [T5](/tasks/transfer) | Skill Transfer Analysis | Causal inference | Point estimate precision, robustness, expert consistency | Confounders, non-random participation order |

## 2. Difficulty Spectrum

```text
Easy  ┌─── T1 Result prediction (abundant data, clear metrics)
      │
      ├─── T3 DNF prediction (class imbalance, but a clear supervision signal)
      │
      ├─── T2 Placement prediction (requires modeling competitor interactions and rule effects)
      │
      ├─── T4 Human limit estimation (requires extrapolation, no direct supervision)
      │
Hard  └─── T5 Skill transfer analysis (causal identification, requires handling confounders)
```

## 3. Unified Task Interface

To guarantee that "the same evaluation code evaluates every model", all tasks follow a unified contract:

```python
class Task:
    name: str
    task_type: Literal["regression", "ranking", "classification", "extreme", "causal"]

    def split(self) -> SplitView: ...        # temporal split view
    def featurize(self, as_of) -> Features:  # decision time is mandatory
        ...
    def metrics(self) -> list[Metric]: ...   # standard metric set
    def baseline(self) -> list[Baseline]: ...# register baselines
    def evaluate(self, model) -> Report: ... # returns metrics + stratified results
```

Key design points:

- The `as_of` argument of `featurize(as_of)` **enforces** leakage prevention
- `evaluate` uniformly returns a `Report` containing **stratified results** and **statistical tests**
- All baselines are comparable through the same `Report`

## 4. Stratified Baseline Design

Every task provides at least three classes of baselines, forming a meaningful comparison spectrum:

| Class | Role |
| --- | --- |
| Trivial baseline | Establishes the lower bound (e.g. historical mean, global majority class) |
| Domain baseline | Reflects current practice (e.g. WCA Psych Sheet, historical DNF rate) |
| Methodological baseline | Tests the gain of more complex methods (DL / GNN / Bayesian / causal) |

The realized inventory — **21 baselines** — is listed in §5; every task ships 4–5 of them.

## 5. Baseline Inventory

The benchmark ships **21 baselines across six methodological families** — one family per subpackage of `src/wca_bench/baselines/`. Every baseline is exported from `baselines/__init__.py`, driven by a `configs/*.yaml` file, run through the rolling-window protocol, and persisted as a report under `examples/`.

| Family (`baselines/`) | Baselines | Count |
| --- | --- | --- |
| `statistical/` | `history_mean`, `kde`, `kde_simulation`, `psych_sheet`, `plackett_luce`, `historical_dnf_rate`, `exponential_decay`, `changepoint`, `gp_evt` | 9 |
| `tree/` | `ridge_log`, `xgboost_log`, `logistic`, `xgboost_dnf` | 4 |
| `bayesian/` | `beta_binomial`, `hierarchical_shrinkage` | 2 |
| `deep/` | `lstm` | 1 |
| `graph/` | `gnn` | 1 |
| `causal/` | `spearman_correlation`, `did_proxy`, `iv_2sls`, `causal_forest` | 4 |
| **Total** | | **21** |

### 5.1 Per-task baseline lists

| Task | Baselines |
| --- | --- |
| [T1 Result Prediction](/tasks/result-prediction) | `history_mean`, `kde`, `ridge_log`, `xgboost_log`, `lstm` |
| [T2 Placement Prediction](/tasks/placement) | `psych_sheet`, `plackett_luce`, `kde_simulation`, `gnn` |
| [T3 DNF Prediction](/tasks/dnf) | `historical_dnf_rate`, `logistic`, `xgboost_dnf`, `beta_binomial` |
| [T4 Human Limit Estimation](/tasks/limit) | `exponential_decay`, `changepoint`, `gp_evt`, `hierarchical_shrinkage` |
| [T5 Skill Transfer Analysis](/tasks/transfer) | `spearman_correlation`, `did_proxy`, `iv_2sls`, `causal_forest` |

Every task therefore exceeds the plan's ≥3-baselines-per-task requirement, and the total of 21 exceeds the plan's target of ≥18.

### 5.2 Running the baselines

```bash
python scripts/run_all_baselines.py --mode small --device cuda   # sampled test set
python scripts/build_leaderboard.py                              # -> examples/leaderboard.{md,csv,json}
python scripts/run_multi_seed.py --seeds 42 43 44 --device cuda  # mean ± std across seeds
```

Device selection (`--device auto|cpu|cuda`, `WCA_BENCH_DEVICE`) and the cost-reporting contract are described in [Compute and Hardware](/evaluation/compute).

### 5.3 Observed Results (seed 42)

The committed leaderboard is a single `small`-mode run at seed 42 on the reference GPU. Full tables: `examples/leaderboard.md`, `examples/leaderboard.csv`, `examples/leaderboard.json`.

| Task | Best baseline | Primary metric | Value |
| --- | --- | --- | --- |
| T1 Result prediction | `xgboost_log` | MAE(log) ↓ | 0.1639 |
| T2 Placement prediction | `kde_simulation` / `plackett_luce` / `psych_sheet` | Kendall's τ ↑ | 0.7673 |
| T3 DNF prediction | `xgboost_dnf` | AUC-PR ↑ | 0.3731 |
| T4 Human limit estimation | `gp_evt` | leave-one-out stability ↓ | 0.9836 |
| T5 Skill transfer | `spearman_correlation` | identifiable event pairs | 413 |

Complete standings:

| Task | Baselines (primary metric) | n |
| --- | --- | --- |
| T1 | `xgboost_log` 0.1639 · `history_mean` 0.6657 · `kde` 0.6657 · `ridge_log` 1.0068 · `lstm` 1.0440 — all MAE(log) | 2196 |
| T2 | `kde_simulation` / `plackett_luce` / `psych_sheet` 0.7673 · `gnn` 0.5670 — Kendall's τ | 2260 |
| T3 | `xgboost_dnf` 0.3731 · `beta_binomial` 0.3725 · `historical_dnf_rate` 0.3591 · `logistic` 0.2290 — AUC-PR | 2260 |
| T4 | `gp_evt` 0.9836 · `exponential_decay` 6485301.0137 · `hierarchical_shrinkage` 9260100.3746 · `changepoint` n/a — leave-one-out stability | — |
| T5 | `spearman_correlation` 413 · `causal_forest` 312 · `iv_2sls` 270 · `did_proxy` 6 — identifiable event pairs | 80000 |

These numbers are **indicative, not final**: `--mode small` samples a handful of competitions inside the test window and subsamples the training split, so the public leaderboard must be re-run on the full dataset under the rolling-window protocol.

### 5.4 Multi-Seed Stability

Primary metrics aggregated over seeds **42 / 43 / 44** (`scripts/run_multi_seed.py --device cuda`). Full table: `examples/multi_seed.md`. Because seeds change which competitions are sampled from the test window, the spread measures the **sampling variance of the evaluation window**, not training instability.

| Task | Model | Metric | mean ± std |
| --- | --- | --- | --- |
| T1 | `xgboost_log` | MAE(log) | 0.1055 ± 0.0417 |
| T1 | `history_mean` / `kde` | MAE(log) | 0.4003 ± 0.1945 |
| T1 | `ridge_log` | MAE(log) | 0.9381 ± 0.0526 |
| T1 | `lstm` | MAE(log) | 0.9436 ± 0.0754 |
| T2 | `psych_sheet` / `plackett_luce` / `kde_simulation` | Kendall's τ | 0.8132 ± 0.0342 |
| T2 | `gnn` | Kendall's τ | 0.7440 ± 0.1258 |
| T3 | `beta_binomial` | AUC-PR | 0.2938 ± 0.0570 |
| T3 | `xgboost_dnf` | AUC-PR | 0.2779 ± 0.0724 |
| T3 | `historical_dnf_rate` | AUC-PR | 0.2631 ± 0.0690 |
| T3 | `logistic` | AUC-PR | 0.1687 ± 0.0429 |
| T4 | `gp_evt` | leave-one-out stability | 0.9836 ± 0.0000 |
| T4 | `exponential_decay` | leave-one-out stability | 6485301.0137 |
| T4 | `hierarchical_shrinkage` | leave-one-out stability | 9260100.3746 |
| T5 | `spearman_correlation` | identifiable pairs | 413 |
| T5 | `causal_forest` | identifiable pairs | 312 |
| T5 | `iv_2sls` | identifiable pairs | 270 |
| T5 | `did_proxy` | identifiable pairs | 2 |

T4 is a deterministic estimator over a fixed world-record series and the T5 transfer matrix is computed from the full training history, so both are stable across seeds (`changepoint` yields no leave-one-out statistic and is omitted).

Two findings worth noting:

- **Domain-aware baselines beat generic deep and graph models.** On T1 the LSTM (1.0440 single-run; 0.9436 ± 0.0754 multi-seed) trails gradient-boosted trees (0.1639; 0.1055 ± 0.0417); on T2 the GNN (0.5670; 0.7440 ± 0.1258) trails the rule-aware Psych Sheet baseline (0.7673; 0.8132 ± 0.0342).
- **Rank stability depends on the task.** T1 and T2 keep the same ordering across seeds, but T3 does not: the single run favours `xgboost_dnf` (0.3731), while the multi-seed mean favours `beta_binomial` (0.2938 ± 0.0570 vs 0.2779 ± 0.0724). The sampling variance of the evaluation window is large enough to reorder close contenders — which is exactly why multi-seed reporting is mandatory.

## 6. Further Reading

- [Task 1: Result Prediction →](/tasks/result-prediction)
- [Task 2: Placement Prediction →](/tasks/placement)
- [Task 3: DNF Prediction →](/tasks/dnf)
- [Task 4: Human Limit Estimation →](/tasks/limit)
- [Task 5: Skill Transfer Analysis →](/tasks/transfer)
