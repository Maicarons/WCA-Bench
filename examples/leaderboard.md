# WCA-Bench Leaderboard

## dnf

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | historical_dnf_rate | auc_pr | 0.3894 | 1468.0 |
| 2 | logistic | auc_pr | 0.1869 | 1468.0 |

## limit

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | exponential_decay | mean_loo_std | 936099.2832 | nan |
| - | changepoint | mean_loo_std | nan | nan |

## placement

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | plackett_luce | kendall_tau | 0.7673 | 2260.0 |
| 1 | psych_sheet | kendall_tau | 0.7673 | 2260.0 |

## result_prediction

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | xgboost_log | mae_log | 0.1908 | 2196.0 |
| 2 | history_mean | mae_log | 0.6657 | 2196.0 |
| 2 | kde | mae_log | 0.6657 | 2196.0 |
| 4 | ridge_log | mae_log | 1.0318 | 2196.0 |

## transfer

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | spearman_correlation | n_identified_pairs | 423.0000 | 80000.0 |
| 2 | did_proxy | n_identified_pairs | 151.0000 | 80000.0 |
