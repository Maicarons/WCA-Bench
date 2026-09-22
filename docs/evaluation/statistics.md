# Statistical Significance Testing

WCA-Bench requires all comparisons between models to use rigorous statistical testing, avoiding the mistake of treating random fluctuation as a methodological gain.

## 1. Testing Methods

| Method | Purpose | Applicable scenario |
| --- | --- | --- |
| **Paired t-test** | Compare the MAE / RMSE difference of two models on the same test set | Two models, paired samples |
| **Bootstrap confidence interval** | Compute the uncertainty of a metric via 1000 resamples | Any metric, unknown distribution |
| **Friedman test + Nemenyi post-hoc test** | Multi-model comparison | ≥ 3 models, multiple datasets/subsets |
| **Effect size reporting** | Report Cohen's d or Cliff's delta | All comparisons |

## 2. Usage Conventions

### 2.1 Paired t-Test

```python
from scipy.stats import ttest_rel

# Use "the error on each competition" as the pairing unit
stat, p = ttest_rel(errors_model_a, errors_model_b)
```

Preconditions:

- A consistent pairing unit (recommended: "competition × event × round")
- Report the mean difference + 95% CI + p-value + effect size

### 2.2 Bootstrap Confidence Intervals

```python
def bootstrap_ci(values, metric_fn, n_boot=1000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    stats = [
        metric_fn(rng.choice(values, size=len(values), replace=True))
        for _ in range(n_boot)
    ]
    lo, hi = np.percentile(stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return metric_fn(values), lo, hi
```

Requirements:

- Fix the random seed (and record it in the report)
- Report the number of resamples (default 1000)
- Provide confidence intervals for stratified results as well

### 2.3 Multi-Model Comparison

When comparing ≥ 3 models:

1. Use the **Friedman test** to determine whether a significant difference exists
2. If significant, use the **Nemenyi post-hoc test** for pairwise comparisons
3. Present the results as a **critical difference diagram**

## 3. Effect Sizes

Avoid relying on p-values alone. Report at least one of the following:

| Effect size | Type | Interpretation |
| --- | --- | --- |
| Cohen's d | Parametric | 0.2 small / 0.5 medium / 0.8 large |
| Cliff's delta | Non-parametric | \|δ\| < 0.147 negligible / < 0.33 small / < 0.474 medium / otherwise large |

## 4. Reporting Specification

Statistical testing is **wired into the task runner**: every evaluated model emits a `significance` block alongside its metrics, so a comparison is never assembled by hand. Submissions additionally ship it as `report/significance.json`.

Every comparison is reported as:

```json
{
  "metric": "mae_log",
  "paired_unit": "competition_event_round",
  "n_pairs": 79,
  "mean_diff": 1.0389,
  "ci95": [0.7556, 1.4728],
  "p_value": 2.93e-07,
  "effect_size": {"name": "cohens_d", "value": 0.8400, "cliffs_delta": 0.7827},
  "test": "paired_t",
  "seed": 42,
  "t_stat": 5.6125,
  "reference": "xgboost_log"
}
```

### 4.1 Required fields

| Field | Meaning |
| --- | --- |
| `metric` | The metric being compared |
| `paired_unit` | The pairing unit (`competition_event_round`) |
| `n_pairs` | Number of paired observations |
| `mean_diff` | Mean paired difference |
| `ci95` | Bootstrap 95% confidence interval of the difference |
| `p_value` | Paired-test p-value |
| `effect_size` | At least one of Cohen's d / Cliff's delta |
| `test` | `paired_t`, or `friedman_nemenyi` for multi-model comparisons |
| `seed` | Seed used for resampling |
| `reference` | The baseline the model is compared against |

### 4.2 Reference model

Each task designates a reference baseline — the strongest domain or methodological baseline for that task — and every other model is compared against it with the task's pairing unit. Cross-report comparability depends on keeping the reference and the pairing unit stable across runs.

The block is carried inside the evaluation report itself; see [Evaluation Protocol and Stratification · Report Contents](/evaluation/protocol#_6-report-contents).

## 5. Common Pitfalls

| Pitfall | Consequence | Avoidance |
| --- | --- | --- |
| Not paired (comparing after aggregation) | Overestimates significance | Use a pairing unit |
| Multiple comparisons without correction | Inflated false positives | Bonferroni / Nemenyi |
| Reporting only p-values, not effect sizes | Significance ≠ importance | Mandatory effect sizes |
| Bootstrap without a fixed seed | Not reproducible | Record the seed |
| Ignoring stratification | Conclusions masked by the dominant group | Stratification + testing |

## 6. Further Reading

- [Reproducibility Requirements →](/evaluation/reproducibility)
- [Evaluation Protocol and Stratification →](/evaluation/protocol)
