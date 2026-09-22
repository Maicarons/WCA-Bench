# WCA-Bench Leaderboard

## dnf

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | xgboost_dnf | auc_pr | 0.3731 | 2260.0 |
| 2 | beta_binomial | auc_pr | 0.3725 | 2260.0 |
| 3 | historical_dnf_rate | auc_pr | 0.3591 | 2260.0 |
| 4 | logistic | auc_pr | 0.2290 | 2260.0 |

## limit

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | gp_evt | mean_loo_std | 0.9836 | nan |
| 2 | exponential_decay | mean_loo_std | 6485301.0137 | nan |
| 3 | hierarchical_shrinkage | mean_loo_std | 9260100.3746 | nan |
| - | changepoint | mean_loo_std | nan | nan |

## placement

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 2 | kde_simulation | kendall_tau | 0.7673 | 2260.0 |
| 2 | plackett_luce | kendall_tau | 0.7673 | 2260.0 |
| 2 | psych_sheet | kendall_tau | 0.7673 | 2260.0 |
| 4 | gnn | kendall_tau | 0.5670 | 2260.0 |

## result_prediction

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | xgboost_log | mae_log | 0.1639 | 2196.0 |
| 2 | history_mean | mae_log | 0.6657 | 2196.0 |
| 2 | kde | mae_log | 0.6657 | 2196.0 |
| 4 | ridge_log | mae_log | 1.0068 | 2196.0 |
| 5 | lstm | mae_log | 1.0440 | 2196.0 |

## transfer

| rank | model | primary | value | n |
| --- | --- | --- | --- | --- |
| 1 | spearman_correlation | n_identified_pairs | 413.0000 | 80000.0 |
| 2 | causal_forest | n_identified_pairs | 312.0000 | 80000.0 |
| 3 | iv_2sls | n_identified_pairs | 270.0000 | 80000.0 |
| 4 | did_proxy | n_identified_pairs | 6.0000 | 80000.0 |
