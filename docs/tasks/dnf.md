# Task 3: DNF Prediction

## Task Definition

Given a competitor's **completed attempt sequence** in a round and the **number of remaining attempts**, predict the probability that a DNF occurs in the competitor's subsequent attempts.

## Inputs

| Category | Field |
| --- | --- |
| Competitor | Competitor ID |
| Sequence | Values of completed attempts (including DNF flags) |
| Context | Current round format, number of remaining attempts |
| History | The competitor's historical DNF rate |
| Time constraint | Decision time `as_of` (mandatory) |

## Outputs

| Output | Type |
| --- | --- |
| DNF probability of the next attempt | Binary probability |
| DNF probability of the round's final result | Probability of a DNF for the whole round |

## Evaluation Metrics

- **AUC-ROC and AUC-PR** (accounting for class imbalance)
- **F1 score and Matthews correlation coefficient (MCC)**
- **Calibration curve (reliability diagram)**
- **Stratified evaluation by round stage** (first round vs final)

::: warning Metric selection under class imbalance
The overall DNF rate is about 2–3%, and in that regime AUC-ROC **overestimates** model ability. AUC-PR and MCC must also be reported, together with the corresponding values of baselines (random / global DNF rate) as a reference.
:::

## Baseline Methods

### Trivial and Domain Baseline

- **Historical DNF rate**: the proportion of DNFs among all of a competitor's historical attempts

### Statistical Baselines

- **Logistic regression**: uses the mean and variance of completed attempts as features
- **Bayesian hierarchical model**: models the DNF rate as a competitor-specific parameter, using a Beta prior for shrinkage estimation

### Methodological Baselines

- **Random forest / XGBoost**: uses competitor features and round context features

## Domain Challenges

### Rare and Uneven

DNFs are **rare events** in WCA data (about 2–3% overall), but their distribution is extremely uneven:

| Event category | DNF rate characteristics |
| --- | --- |
| Blindfolded / multi-blind | Far above average, with many "all-DNF" rounds |
| Speed events (3x3 etc.) | Lower and stable |
| Fewest moves | Distinctive: timeouts or rule violations cause DNFs |

### Sequential Dependence

The occurrence of a DNF exhibits **sequential dependence** — one DNF may lead a competitor, in subsequent attempts, to:

- Adopt a more conservative strategy (lowering the DNF rate), or
- Experience a psychological collapse (raising the DNF rate)

This two-way effect requires models to explicitly model **state evolution within a round** rather than relying on static features alone.

### Rule Dependence

In ao5, the risk structure after "already 1 DNF" is completely different from that after "0 DNFs" (after one DNF there is zero margin for error).

## Hard Sample Subset

To prevent benchmark saturation (for example, losing discriminative power when AUC > 0.95), a **high-uncertainty subset** is additionally reported:

```text
Definition of the high-uncertainty subset:
    Competitor historical DNF rate ∈ [0.1, 0.3]
```

All metrics are reported separately on this subset, keeping the task discriminative as the benchmark evolves.

## Deliverables and Acceptance

- Definition document (all five elements present)
- ≥ 4 runnable baselines
- AUC-ROC / AUC-PR / MCC / calibration curve + stratified report
- Independent results for the high-uncertainty subset

## Further Reading

- [Task 4: Human Limit Estimation →](/tasks/limit)
- [Risks and Mitigation · Benchmark Saturation Risks →](/plan/risks)
