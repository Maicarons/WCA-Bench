# Phase 2: Task Definition and Baseline Implementation (Months 4–6)

> **Objective**: Formalize the five tasks, implement the complete set of baselines, and produce an initial leaderboard.
> **Exit milestones**: [M2 Task Definition Frozen](/plan/roadmap#m2-·-task-definition-frozen-month-5), [M3 Baseline Experiments Complete](/plan/roadmap#m3-·-baseline-experiments-complete-month-6)

## 1. Phase Objectives

- Formally define the problem setting and evaluation metrics of the five tasks
- Implement baseline models for each task (classical statistics + simple deep learning)
- Run baseline experiments and generate the initial leaderboard
- Write the task documentation

## 2. Work Breakdown (WBS)

### 2.1 Evaluation Framework Tasks

| Task ID | Task name | Weeks | Prerequisites | Deliverables |
| --- | --- | --- | --- | --- |
| P2-T1 | Unified Task interface | W13 | M1 | `tasks/base.py` |
| P2-T2 | Evaluation metrics library | W13–W14 | P2-T1 | `evaluation/metrics.py` |
| P2-T3 | Rolling-window protocol | W14–W15 | P2-T2 | `evaluation/protocol.py` |
| P2-T4 | Four-way stratified evaluation | W15–W16 | P2-T3 | `evaluation/stratified.py` |
| P2-T5 | Statistical tests and effect sizes | W16 | P2-T4 | `evaluation/significance.py` |
| P2-T6 | Task definition documentation freeze | W17–W18 | P2-T1~T5 | `docs/tasks/*` (M2) |

### 2.2 Task and Baseline Implementation

| Task ID | Task name | Weeks | Prerequisites | Deliverables |
| --- | --- | --- | --- | --- |
| P2-T7 | T1 Result prediction + baselines | W18–W20 | P2-T3 | `tasks/result_prediction/` + 4 baselines |
| P2-T8 | T2 Placement prediction + baselines | W19–W21 | P2-T3 | `tasks/placement/` + 4 baselines |
| P2-T9 | T3 DNF prediction + baselines | W20–W22 | P2-T3 | `tasks/dnf/` + 4 baselines |
| P2-T10 | T4 Limit estimation + baselines | W21–W23 | P2-T3 | `tasks/limit/` + 4 baselines |
| P2-T11 | T5 Skill transfer + baselines | W22–W24 | P2-T3 | `tasks/transfer/` + 4 baselines |
| P2-T12 | Experiment management and configuration | W19–W24 | P2-T7 | `configs/*` + W&B/MLflow integration |
| P2-T13 | Leaderboard generation | W24–W25 | P2-T7~T12 | `scripts/build_leaderboard.py` + leaderboard (M3) |

> Weeks continue from Phase 1 (W13 = the project's 13th week); the phase lasts 12 weeks (W13–W24), including a 1-week buffer.

## 3. Detailed Task Descriptions

### P2-T1 · Unified Task Interface

```python
class Task(Protocol):
    name: str
    task_type: str
    def split(self) -> SplitView: ...
    def featurize(self, as_of) -> Features: ...
    def metrics(self) -> list[Metric]: ...
    def baseline(self) -> list[Baseline]: ...
    def evaluate(self, model) -> Report: ...
```

- **Acceptance**: the `evaluate` method of every task returns a unified `Report` structure

### P2-T2 · Evaluation Metrics Library

| Task | Metrics |
| --- | --- |
| T1 | MAE(log), RMSE(log), interval coverage |
| T2 | Kendall's τ, top-3 accuracy, Brier |
| T3 | AUC-ROC, AUC-PR, F1, MCC, calibration |
| T4 | Leave-one-out stability, interval coverage |
| T5 | Point estimate precision, robustness |

- **Acceptance**: every metric has unit tests and benchmark cases with known inputs and outputs

### P2-T3 · Rolling-Window Protocol

- Implement the time-advancing evaluation loop
- Injection of frozen statistics
- The `assert_no_leakage` assertion utility
- **Acceptance**: the protocol is verifiably leakage-free on synthetic data

### P2-T4 · Four-Way Stratified Evaluation

- Four-way stratification by event / competitor skill level / time / region
- Definition and extraction of hard sample subsets
- Cold-start samples reported separately
- **Acceptance**: stratified results can be fully recomputed from the raw predictions

### P2-T5 · Statistical Tests and Effect Sizes

- Paired t-test, bootstrap CI (1000 resamples), Friedman + Nemenyi
- Cohen's d / Cliff's delta
- **Acceptance**: `significance.json` is emitted according to the [specification](/evaluation/statistics#_4-reporting-specification)

### P2-T6 · Task Definition Documentation Freeze (M2)

- All five elements present in the five task documents (definition/inputs-outputs/metrics/baselines/challenges)
- Domain challenges described explicitly
- **Acceptance**: review passed and the version marked as frozen

### P2-T7 ~ P2-T11 · Implementation of the Five Tasks

The implementation pattern is identical for every task:

```text
1. Implement the Task subclass (split / featurize / metrics)
2. Implement the trivial baseline (establishing the lower bound)
3. Implement the domain baseline (reflecting current practice)
4. Implement methodological baselines (DL / GNN / Bayesian / causal)
5. Run the rolling-window evaluation
6. Generate the stratified report + statistical tests
```

The baseline list for each task is given in the [Task Suite](/tasks/).

### P2-T12 · Experiment Management and Configuration

- All experiments are driven by `configs/*.yaml`
- Integrate W&B or MLflow to record metrics, configurations, and artifacts
- Fix random seeds and record them
- **Acceptance**: any experiment can be reproduced from its configuration with a single command

### P2-T13 · Leaderboard Generation (M3)

- Aggregate each task's `report/` into the overall leaderboard
- The leaderboard contains: primary metrics, stratified metrics, compute cost
- **Acceptance**: all ≥ 18 baselines are included and results can be recomputed

## 4. Phase Deliverables

| ID | Deliverable | Corresponding tasks |
| --- | --- | --- |
| D4 | Five task definitions and evaluation protocol | P2-T1 ~ P2-T6 |
| D5 | Baseline implementations and results | P2-T7 ~ P2-T12 |
| D6 | Leaderboard and submission specification | P2-T13 |

## 5. Phase Acceptance Criteria

- [ ] All five task definition documents contain the five elements and have passed review (M2)
- [ ] ≥ 3 runnable baselines per task, ≥ 18 in total
- [ ] All baselines run end-to-end in CI small-sample mode
- [ ] Every baseline produces a complete `report/` (including four-way stratification and significance)
- [ ] The leaderboard can be rebuilt with a single script
- [ ] All experiment configurations are reproducible with a single command (reproduction level ≥ L2)

## 6. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Sequence model training overruns | Phase delay | Start early, cap the compute budget, allow degrading to a smaller model |
| GNN graph construction is complex | Task 2 delayed | Ship non-GNN baselines first; add the GNN incrementally |
| Metric implementation errors | Untrustworthy results | Metric unit tests + alignment with official/known implementations |
| Repeated changes to task definitions | Affects downstream work | Set the M2 freeze point; route changes through a versioned process |

## 7. Further Reading

- [Phase 3: Benchmark Release →](/plan/phase-3)
- [Acceptance Criteria →](/plan/acceptance)
