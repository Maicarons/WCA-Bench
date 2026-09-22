# Task 2: Placement Prediction

## Task Definition

Given the historical results of **all participating competitors** in a competition, predict each competitor's ranking in that round.

## Inputs

| Category | Field |
| --- | --- |
| Competition context | Competition ID, event ID, round type |
| Competitor set | Historical result features of all participating competitors |
| Time constraint | Decision time `as_of` (mandatory) |

## Outputs

| Output | Type |
| --- | --- |
| Predicted placement of each competitor | Integer |
| Placement probability distribution | P(rank = k) |
| Podium probability | P(rank ≤ 3) |

## Evaluation Metrics

- **Kendall's τ** (rank correlation coefficient)
- **Top-3 accuracy** (size of the intersection between the predicted podium and the actual podium)
- **Brier score of placement probabilities**
- **Comparison against the WCA Psych Sheet**

::: tip Why compare against the Psych Sheet
The ranking system currently used officially by the WCA (the Psych Sheet) is **based only on a competitor's best Ao5**, ignoring variance and consistency. It is a natural strong domain baseline that reveals the true value of "introducing distributional information".
:::

## Baseline Methods

### Domain Baseline

- **Psych Sheet baseline**: rank by competitors' historical best Ao5

### Statistical Baselines

- **Kernel density estimation simulation**: build a KDE for each competitor, simulate round results via Monte Carlo, and derive the placement distribution
- **Plackett-Luce model**: models the ranking as a probability over "strength" parameters of competitors

### Methodological Baselines

- **Graph neural network (GNN)**: builds a competitor–competition heterogeneous graph to learn the adversarial relationships among competitors

## Domain Challenges

### Interaction Effects Between Competitors

The core difficulty of placement prediction lies in **interaction effects between competitors** — the same competitor may perform differently against different opponents. This requires the model not only to estimate "absolute strength" but also to model **relative competitive relationships**.

### Rule Effects

Round formats (such as the ao5 trimming mechanism) mean that **the impact of a single DNF on the final placement is amplified**, requiring the model to explicitly model this rule effect.

| Case | Impact on ao5 |
| --- | --- |
| 1 DNF | Usually discarded as the worst attempt, with limited impact |
| 2 DNFs | A DNF for the whole round; the placement collapses |
| 0 DNFs but one mistake | The mistake is discarded, and the average may look better than the competitor's real level |

### Competition Size Variation

The number of participants in the same event varies enormously across competitions (from a handful to several hundred), requiring the handling of **variable-size ranking**.

## Method and Data Structures

```text
Competitor ──participates in──► Competition ──round──► set of competitors in that round
  │
  └─ historical result sequence (before as_of)
```

The GNN baseline models `(competitor, competition, round)` as heterogeneous graph nodes, with edges representing "competition in the same round of the same event".

## Deliverables and Acceptance

- Definition document (all five elements present)
- ≥ 4 runnable baselines (including the Psych Sheet)
- Stratified report on Kendall's τ and Brier
- A significance comparison conclusion against the official Psych Sheet

## Further Reading

- [Task 3: DNF Prediction →](/tasks/dnf)
- [Evaluation Framework · Statistical Significance Testing →](/evaluation/statistics)
