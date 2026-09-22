# Data Splitting Strategy

## 1. Principle: Temporal Splitting, Not Random Splitting

WCA-Bench adopts **temporal splitting** rather than random splitting, which is a basic principle of sports data analysis:

- Random splitting leaks future information (adjacent competitions of the same competitor are highly correlated)
- Temporal splitting simulates the real deployment scenario (using the past to predict the future)
- Temporal splitting ensures that the assessment of a model's generalization ability is not affected by future information leakage

## 2. Splitting Scheme

| Set | Time range | Purpose |
| --- | --- | --- |
| **Training set** | 2003 – 2022 | Model training and estimation of feature statistics |
| **Validation set** | 2023 – 2024 | Hyperparameter tuning and model selection |
| **Test set** | 2025 – 2026 | Final evaluation (fixed window) |

At the same time, each competitor's **complete sequence of competition history** is preserved to support longitudinal analysis.

## 3. Temporal Strata

The test set is further divided into three subsets to evaluate the temporal robustness of models:

| Subset | Time window |
| --- | --- |
| Test-A | First half of 2025 |
| Test-B | Second half of 2025 |
| Test-C | First half of 2026 |

## 4. Rolling Window Evaluation

WCA-Bench adopts a **rolling window evaluation** protocol that simulates the real deployment scenario:

```text
For every competition c in the test set:
    Available data = { all records with competition_date < c.date }
    Frozen statistics = historical means / world records / event baselines computed on the training period
    Prediction targets = the competitor's best / average / rank / DNF in that round of c
```

Key constraints:

- **No form of future information leakage**
- Benchmark statistics are **frozen** during the test window and do not update as the test set advances
- Follows best practice for leakage prevention in sports data analysis

## 5. Split Artifacts

```text
data/splits/
├── train_ids.parquet      # Result row IDs of the training set
├── val_ids.parquet        # Result row IDs of the validation set
├── test_ids.parquet       # Result row IDs of the test set
├── test_time_slices.json  # Temporal boundaries of Test-A / B / C
├── person_history.parquet # Each competitor's time-ordered sequence of participations
└── frozen_stats.parquet   # Frozen benchmark statistics (computed on the training period)
```

## 6. Boundary Cases

| Case | Handling |
| --- | --- |
| A competitor's first appearance falls in the test period | Marked as "cold start" and reported separately (no history to rely on) |
| An event's first edition falls in the test period | Removed from the comparable samples of the per-event stratum and described separately |
| A competition spans the new year (e.g. 2024-12-31 ~ 2025-01-02) | Categorized by its start date |
| Future revisions in the data (results are updated) | Pinned to the export snapshot version and recorded in the data card |

## 7. Frozen Test Set and Extended Test Set

Because the WCA database keeps being updated, competition data from 2026 onward is continuously added:

- The **main leaderboard** is always based on the fixed 2025–2026 test window
- Newly added data is released separately as an "**Extended Test Set**" and reported separately
- This follows the convention of time-series benchmarks and preserves the historical comparability of the leaderboard

## 8. Further Reading

- [Evaluation Protocol and Stratification →](/evaluation/protocol)
- [Reproducibility Requirements →](/evaluation/reproducibility)
- [Risks and Mitigation · Data Risks →](/plan/risks)
