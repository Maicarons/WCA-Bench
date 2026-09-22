# Task 4: Human Limit Estimation

## Task Definition

Based on the **historical world record sequence** of each event, estimate the theoretical human performance limit for that event and predict the time horizon over which the limit will be reached.

## Inputs

| Category | Field |
| --- | --- |
| Sequence | The world record time series of each event (date, result value) |
| Event features | Mean result, result variance, length of the event's history |

## Outputs

| Output | Type |
| --- | --- |
| Point estimate of the limit | Continuous value |
| Posterior distribution of the limit | Probability distribution |
| Expected year of reaching the limit | Year + interval |
| Uncertainty interval | Confidence / credible interval |

## Evaluation Metrics

- **Stability of the limit estimate** (variance under leave-one-out cross-validation)
- **Coverage of prediction intervals**
- **Consistency with known domain knowledge**

::: info Reference point
Known domain knowledge puts the 3x3 limit estimate at approximately **2.37 seconds**, with convergence around **2036**, which can serve as one anchor for consistency checks.
:::

## Baseline Methods

### Statistical Baselines

- **Exponential decay model**: assumes results approach the limit exponentially

### Methodological Baselines

- **Gaussian process regression + extreme value theory**: uses a GP to model the non-linear trend and EVT to model extreme observations
- **Bayesian hierarchical extreme value model**: treats each event's limit as a random variable drawn from a hyper-distribution
- **Change point detection**: identifies structural changes in the rate of result improvement

## Domain Challenges

### Extrapolation Risk

Human limit estimation faces **extrapolation risk** — historical data may fail to capture the step changes brought about by future training methods or hardware innovation (for example, new magnetic cube structures or revolutionary training systems).

### Vastly Different Data Density

Limit estimation across events requires **different model complexity**:

| Event category | Data situation | Modeling strategy |
| --- | --- | --- |
| 3x3 | 23 years of dense data | Complex models are viable (GP + EVT) |
| Emerging events | Possibly fewer than 50 data points | Require strong priors or hierarchical information borrowing |

### No Direct Supervision Signal

The "true limit" is **unobservable**, so evaluation relies on:

- **Stability** under leave-one-out cross-validation
- **Consistency** with domain judgment
- **Convergence** across different methods

## Modeling Framework

```text
Observation: world record time series { (t_i, y_i) }
Model: y(t) = L + (y_0 - L) · exp(-λ · g(t)) + ε(t)
       where L is the limit, g(t) is the technological progress function, and ε is noise
Inference: Bayesian posterior p(L, λ, params | data)
Output: posterior distribution of L + distribution of the convergence year
```

## Deliverables and Acceptance

- Definition document (all five elements present)
- ≥ 4 runnable baselines
- Leave-one-out stability report
- Comparative analysis against domain knowledge

## Further Reading

- [Task 5: Skill Transfer Analysis →](/tasks/transfer)
- [Task Suite · Overview →](/tasks/)
