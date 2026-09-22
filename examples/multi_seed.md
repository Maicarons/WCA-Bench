# WCA-Bench multi-seed results

- Mode: `small`
- Seeds: **42, 43, 44**
- Device: **CUDA** — NVIDIA GeForce RTX 4060 Laptop GPU (8 GB), CUDA 13.0, torch 2.13.0+cu130
- Aggregation: the primary metric is reported as **mean ± standard deviation** across the three seeds
- Coverage: all 21 baselines across the five tasks
- Command: `python scripts/run_multi_seed.py --seeds 42 43 44 --mode small --device cuda`

Seeds change which competitions are sampled from the test window, so the spread below measures the
**sampling variance of the evaluation window**, not training instability.

## dnf

| model | metric | mean ± std | n_seeds |
| --- | --- | --- | --- |
| beta_binomial | auc_pr | 0.2938 ± 0.0570 | 3 |
| xgboost_dnf | auc_pr | 0.2779 ± 0.0724 | 3 |
| historical_dnf_rate | auc_pr | 0.2631 ± 0.0690 | 3 |
| logistic | auc_pr | 0.1687 ± 0.0429 | 3 |

## limit

| model | metric | mean ± std | n_seeds |
| --- | --- | --- | --- |
| hierarchical_shrinkage | mean_loo_std | 9260100.3746 ± 0.0000 | 3 |
| exponential_decay | mean_loo_std | 6485301.0137 ± 0.0000 | 3 |
| gp_evt | mean_loo_std | 0.9836 ± 0.0000 | 3 |

> Task 4 is a deterministic estimator over the fixed world-record series, so it has zero variance
> across seeds; `changepoint` produces no leave-one-out statistic and is omitted.

## placement

| model | metric | mean ± std | n_seeds |
| --- | --- | --- | --- |
| kde_simulation | kendall_tau | 0.8132 ± 0.0342 | 3 |
| plackett_luce | kendall_tau | 0.8132 ± 0.0342 | 3 |
| psych_sheet | kendall_tau | 0.8132 ± 0.0342 | 3 |
| gnn | kendall_tau | 0.7440 ± 0.1258 | 3 |

## result_prediction

| model | metric | mean ± std | n_seeds |
| --- | --- | --- | --- |
| lstm | mae_log | 0.9436 ± 0.0754 | 3 |
| ridge_log | mae_log | 0.9381 ± 0.0526 | 3 |
| history_mean | mae_log | 0.4003 ± 0.1945 | 3 |
| kde | mae_log | 0.4003 ± 0.1945 | 3 |
| xgboost_log | mae_log | 0.1055 ± 0.0417 | 3 |

## transfer

| model | metric | mean ± std | n_seeds |
| --- | --- | --- | --- |
| spearman_correlation | n_identified_pairs | 413.0000 ± 0.0000 | 3 |
| causal_forest | n_identified_pairs | 312.0000 ± 0.0000 | 3 |
| iv_2sls | n_identified_pairs | 270.0000 ± 0.0000 | 3 |
| did_proxy | n_identified_pairs | 2.0000 ± 0.0000 | 3 |

> The transfer matrix is computed from the full training history rather than from the sampled test
> competitions, so the number of identifiable event pairs is stable across seeds.

## Reference

Machine-readable output: `outputs/multi_seed/multi_seed.json`.
Single-run leaderboard: [`leaderboard.md`](leaderboard.md).
