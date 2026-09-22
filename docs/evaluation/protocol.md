# Evaluation Protocol and Stratification

## 1. Evaluation Protocol

WCA-Bench adopts a **rolling window evaluation** protocol that simulates the real deployment scenario:

- For **every competition** in the test set, the model may only access data preceding that competition
- Benchmark statistics (such as a competitor's historical mean and an event's world record) are computed on **training-period** data and **frozen** throughout the test window
- **No form of future information leakage**

This protocol follows best practice for leakage prevention in sports data analysis.

### 1.1 Protocol Pseudocode

```python
def rolling_evaluation(model, test_competitions, frozen_stats):
    reports = []
    for comp in sorted(test_competitions, key=lambda c: c.date):
        # 1. Build features using only data before as_of
        features = featurize(as_of=comp.date, frozen_stats=frozen_stats)
        # 2. Assert that there is no leakage
        assert_no_leakage(features, target_date=comp.date)
        # 3. Predict and evaluate
        preds = model.predict(features)
        reports.append(evaluate(preds, comp.ground_truth))
    return aggregate(reports)
```

### 1.2 Frozen Statistics

| Statistic | Computed from | Frozen at |
| --- | --- | --- |
| Competitor historical mean / variance | Training period (≤ 2022) | Throughout the test window |
| Event world records | Training period | Throughout the test window |
| Event baseline distributions | Training period | Throughout the test window |
| Competitor skill percentile thresholds | Training period | Throughout the test window |

## 2. Stratified Evaluation

To prevent evaluation results from being **masked by dominant groups** in the data, WCA-Bench requires stratified evaluation reports on all tasks.

### 2.1 Stratification by Event

The 17 WCA events differ enormously in data volume and difficulty. 3x3 has the most data, while events such as 4x4 blindfolded and multi-blind have limited sample sizes. Stratified evaluation reveals a model's **generalization ability across events**.

| Group | Events |
| --- | --- |
| Cubic speed events | 3x3, 4x4, 5x5, 6x6, 7x7 |
| Non-cubic and side events | 3x3 one-handed, 3x3 blindfolded, fewest moves, clock, skewb, pyraminx, SQ1 |
| Blindfolded | 4x4 blindfolded, 5x5 blindfolded, multi-blind |
| Other | 3x3 with feet (if still valid), etc. |

### 2.2 Stratification by Competitor Skill Level

Competitors are divided into four groups by the percentile of their historical results:

| Group | Percentile |
| --- | --- |
| Novice | Bottom 25% |
| Intermediate | 25% – 75% |
| Advanced | 75% – 95% |
| Elite | Top 5% |

Competitors at different levels differ systematically in **result stability, DNF rate, and participation frequency**.

### 2.3 Stratification by Time

The test set is divided into three subsets to evaluate a model's **temporal robustness**:

| Subset | Time window |
| --- | --- |
| Test-A | First half of 2025 |
| Test-B | Second half of 2025 |
| Test-C | First half of 2026 |

### 2.4 Stratification by Region

Stratify by the competitor's continent to evaluate a model's **cross-cultural generalization ability**:

```text
Asia / Europe / North America / South America / Oceania / Africa
```

## 3. Hard Sample Subsets

To prevent benchmark saturation, tasks must additionally report hard sample subsets:

| Task | Definition of the hard sample |
| --- | --- |
| T3 DNF | Competitor historical DNF rate ∈ [0.1, 0.3] |
| T1 Result | Recent result variance in the upper quartile |
| T2 Placement | Historical result difference among the top 8 competitors < threshold |
| T5 Transfer | Event pairs whose sample size is in the lower quartile |

## 4. Cold-Start Handling

| Case | Handling |
| --- | --- |
| A competitor's first competition | Marked as a cold start and reported separately (not mixed into the primary metric) |
| An event's first edition | Removed from the comparable samples of the per-event stratum |
| Participants from a new region | Reported separately, with the sample size stated |

## 5. Report Consistency Requirements

- All models use the **same split indices** (`data/splits/`)
- All models use the **same frozen statistics**
- Stratified results must be traceable back to the original per-competition predictions
- Statistical significance is **part of the report**, not an afterthought — see §6
- Missing-value handling strategies must be stated explicitly in the report

## 6. Report Contents

Every evaluated model emits one report object. The `significance` block is **produced by the task runner** and persisted with the metrics; it is never added by hand afterwards.

| Field | Content |
| --- | --- |
| `task`, `model` | Task and baseline identifiers |
| `overall` | Whole-dataset metrics |
| `stratified` | `by_event`, `by_skill_level`, `by_time_slice`, `by_continent` |
| `hard_subset` | Hard-sample-subset metrics (§3) |
| `significance` | Paired test against the reference model of that task: metric, pairing unit, `n_pairs`, `mean_diff`, `ci95`, `p_value`, effect size, test name, seed, reference |
| `cost` | Compute cost — device, wall clock, CPU/GPU hours (see [Compute and Hardware · Cost Reporting Specification](/evaluation/compute#_4-cost-reporting-specification)) |
| `extras` | Cold-start summary and further diagnostics |
| `seed`, `data_summary` | Seed and dataset provenance, where the runner records them |

The `significance` block is computed against the task's reference baseline (for example `xgboost_log` for T1) using the pairing unit declared for that task. Statistical definitions, required fields, and effect sizes are specified in [Statistical Significance Testing · Reporting Specification](/evaluation/statistics#_4-reporting-specification).

## 7. Further Reading

- [Statistical Significance Testing →](/evaluation/statistics)
- [Reproducibility Requirements →](/evaluation/reproducibility)
- [Data Splitting Strategy →](/data/splits)
