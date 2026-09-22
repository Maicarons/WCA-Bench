# Task 5: Skill Transfer Analysis

## Task Definition

Quantify how a competitor's **improvement in one event** **causally** affects their **performance in another event**.

## Inputs

| Category | Field |
| --- | --- |
| Multi-event records | The competitor's multi-event participation records (timestamp, event, result) |
| Time annotations | The time at which the competitor first participated in each event |

## Outputs

| Output | Type |
| --- | --- |
| Skill transfer matrix | 17 × 17; the causal transfer effect from event i to event j |
| Confidence intervals of transfer effects | Interval estimates |

## Evaluation Metrics

- **Precision of point estimates of transfer effects** (compared against held-out data)
- **Robustness of causal effects** (stability across different subsamples)
- **Consistency with domain expert judgment**

## Baseline Methods

### Correlation Baseline

- **Correlation analysis**: Pearson / Spearman correlation of results across events

### Causal Method Baselines

- **Difference-in-differences (DID)**: treats a competitor's first participation in an event as the "treatment" and compares the subsequent performance of the treated and control groups
- **Instrumental variables (IV)**: uses "the first edition of the event held in the competitor's country" as an instrument
- **Causal forest**: uses a causal forest to estimate heterogeneous treatment effects

## Domain Challenges

### Confounders

The core difficulty of skill transfer analysis lies in **confounders**:

> A competitor's results in 3x3 and 4x4 may both be influenced by "talent" and "training investment"; simple correlation cannot separate causal relationships.

| Confounder | Direction of influence |
| --- | --- |
| Talent (G) | Improves performance in multiple events simultaneously → spurious positive transfer |
| Training investment (E) | Improves performance in multiple events simultaneously → spurious positive transfer |
| Age / experience | Grows over time → requires time fixed effects |

### Non-Random Event Participation Order

In WCA data, the order in which a competitor takes up events is **not randomly assigned** — a competitor may choose to take up related events earlier because they are already good at a certain event (self-selection bias).

```text
Illustration of selection bias:
   A person strong at 3x3 → starts practicing 4x4 earlier → observes 3x3↑ accompanied by 4x4↑
   → mistakenly concluded as "3x3 training causes 4x4 improvement"
```

### Sparsity and Imbalance

Some event pairs share very few competitors in common, leading to extremely high variance in effect estimates. This requires:

- Hierarchical shrinkage (borrowing information from similar event pairs)
- Explicit "unidentifiable" flags (no strong conclusions when samples are insufficient)

## Identification Strategies

| Strategy | Assumption | Strength |
| --- | --- | --- |
| Correlation | No confounding (a strong assumption; only for reference) | Weak |
| DID | Parallel trends assumption | Medium |
| IV | Exogeneity of the instrument | Strong (but requires testing) |
| Causal forest | No unobserved confounding | Strong |

## Deliverables and Acceptance

- Definition document (all five elements present)
- ≥ 4 runnable baselines
- 17 × 17 transfer matrix + confidence intervals
- Robustness analysis (subsamples / sensitivity)
- Explicit discussion of self-selection bias

## Further Reading

- [Evaluation Framework · Overview →](/evaluation/)
- [Publication Strategy →](/plan/publication)
