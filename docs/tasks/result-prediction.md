# Task 1: Result Prediction

## Task Definition

Given a competitor's pre-competition history of results, participation frequency, cross-event experience, age, nationality, and similar information, predict the competitor's best and average results in **a given round of a given event at a given competition**.

## Inputs

| Category | Field |
| --- | --- |
| Identifiers | Competitor ID, competition ID, event ID, round type |
| Sequence | Historical result sequence (the most recent N attempts) |
| Static features | Age, gender, nationality, total number of competitions |
| Time constraint | Decision time `as_of` (mandatory) |

## Outputs

| Output | Type |
| --- | --- |
| best result | Continuous value |
| average result | Continuous value (if the round format is ao5 or mo3) |
| Result distribution parameters | Mean and variance |

## Evaluation Metrics

- **MAE and RMSE** (computed after a logarithmic transform of the result values)
- **Calibration error** (coverage of prediction intervals)
- **Stratified evaluation by competitor skill level** (novice, intermediate, advanced, elite)

| Metric | Description |
| --- | --- |
| MAE (log) | Primary metric; the log domain prevents large-value events from dominating |
| RMSE (log) | More sensitive to large errors |
| Interval coverage | Checks whether prediction intervals are trustworthy (e.g. a 90% interval actually covers close to 90%) |

## Baseline Methods

### Trivial Baseline

- **Historical mean**: the mean of the competitor's most recent 25 attempts

### Domain and Statistical Baselines

- **Linear regression**: linear extrapolation from recent results
- **Kernel density estimation (KDE)**: models the competitor's result distribution and simulates round results via bootstrap

### Methodological Baselines

- **LSTM / Transformer**: sequence-to-sequence encoder–decoder architectures

## Domain Challenges

### Non-Stationarity of Performance

Result prediction must handle the **non-stationarity** of a competitor's performance — a competitor may experience step changes in results due to:

- Improvements in training methods
- Injury
- Equipment changes (e.g. a new cube)

### Variance Differences Across Events

Result distributions differ drastically across events (3x3 and 7x7 have different variances), requiring **event-specific normalization strategies**.

| Event | Order of magnitude | Variance characteristics |
| --- | --- | --- |
| 3x3 | Seconds | Relatively large variance (wide span from novice to elite) |
| 7x7 | Minutes | Relatively small variance (high barrier to entry) |
| Fewest moves | Move count | Discrete, skewed distribution |

## Leakage-Free Requirements

```text
Allowed for feature construction: all records with competition_date < as_of
Forbidden: all records at or after the target competition, including other competitors' results in that round
Benchmark statistics: competitor historical means are computed on the training period and then frozen
```

## Deliverables and Acceptance

- Definition document (all five elements present: inputs/outputs/metrics/baselines/challenges)
- ≥ 4 runnable baselines
- Primary metric + stratified evaluation report
- Leakage-prevention assertion tests pass

## Further Reading

- [Task 2: Placement Prediction →](/tasks/placement)
- [Evaluation Protocol and Stratification →](/evaluation/protocol)
