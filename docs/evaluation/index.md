# Evaluation Framework · Overview

The evaluation framework is the core of the benchmark's credibility. This chapter describes the evaluation protocol, the stratification strategy, statistical testing, and reproducibility requirements.

## 1. Chapter Structure

| Chapter | Contents |
| --- | --- |
| [Evaluation Protocol and Stratification](/evaluation/protocol) | Rolling-window protocol, four-way stratification, hard sample subsets |
| [Statistical Significance Testing](/evaluation/statistics) | Paired tests, bootstrap, Friedman, effect sizes |
| [Reproducibility Requirements](/evaluation/reproducibility) | Code, seeds, weights, compute report |

## 2. Four Pillars

```text
┌──────────────────────┐
│ 1. Leakage-free      │  Rolling window + frozen statistics
├──────────────────────┤
│ 2. Stratified        │  Event / level / time / region
├──────────────────────┤
│ 3. Statistical rigor │  Significance tests + effect sizes
├──────────────────────┤
│ 4. Reproducible      │  Code + data + weights + compute
└──────────────────────┘
```

## 3. Why Stratification and Statistical Testing

| Risk | Countermeasure |
| --- | --- |
| Conclusions masked by the dominant group (3x3 has far more data than other events) | Stratify by event |
| Averages masking subgroup differences (elites and novices behave differently) | Stratify by competitor skill level |
| Models sensitive to temporal drift | Stratify by time |
| Unknown cross-cultural generalization ability | Stratify by region |
| Incidental performance differences mistaken for real gains | Statistical testing + effect sizes |
| Results not reproducible by third parties | Reproducibility checklist |

## 4. Report Template

Every model submission must include the following report structure:

```text
report/
├── overall.json          # Whole-dataset metrics
├── by_event.json         # Stratified by event
├── by_skill_level.json   # Stratified by competitor skill level
├── by_time_slice.json    # Stratified by time (Test-A/B/C)
├── by_continent.json     # Stratified by region
├── calibration.json      # Calibration / Bootstrap CI
├── significance.json     # Statistical tests against baselines
└── cost.json             # Inference and training compute cost
```

## 5. Further Reading

- [Evaluation Protocol and Stratification →](/evaluation/protocol)
- [Statistical Significance Testing →](/evaluation/statistics)
- [Reproducibility Requirements →](/evaluation/reproducibility)
