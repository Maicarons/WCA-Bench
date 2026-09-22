---
license: Apache-2.0
language:
- en
pretty_name: WCA-Bench
size_categories:
- 1M<n<10M
task_categories:
- tabular-regression
- tabular-classification
- time-series-forecasting
- other
tags:
- benchmark
- sports-analytics
- speedcubing
- wca
- tabular
- time-series
- causal-inference
- machine-learning
---

# WCA-Bench (ModelScope Dataset Card)

## 中文摘要

WCA-Bench 是首个基于**世界魔方协会（WCA）公开比赛数据**的综合性机器学习基准，涵盖
成绩预测（T1）、名次预测（T2）、DNF 预测（T3）、人类极限估计（T4）、技能迁移分析（T5）
五类任务。数据来自 WCA 官方 Results Export v2.0.2（约 690 万条 results，2003–2026），
以解码后的 Parquet 表、冻结训练期统计量与 train/val/test 时间划分索引的形式发布，并提供
无时间泄漏的统一评估协议。代码采用 Apache-2.0，数据版权归 World Cube Association 所有。

## English Summary

**WCA-Bench** is the first comprehensive machine-learning benchmark built on public
[World Cube Association](https://www.worldcubeassociation.org/) competition data. It
covers five tasks — result prediction (T1), placement prediction (T2), DNF prediction
(T3), human-limit estimation (T4), and skill-transfer analysis (T5) — under a
leakage-free temporal evaluation protocol.

- **Source:** WCA Results Database Export, format v2.0.2 (`persons`, `competitions`,
  `results`, `result_attempts`, `scrambles`, `events`, `formats`, `round_types`,
  `countries`, `continents`, `championships`).
- **Scale:** ~6.9M results, ~298k contestants, ~18.7k competitions (2003–2026).
- **Splits:** train 2003–2022, validation 2023–2024, test 2025–2026 (Test-A/B/C).
- **Code license:** Apache-2.0. **Data rights:** World Cube Association.

## Repository Layout

```text
.
├── README.md
├── configuration.json
├── dataset_meta.json
├── data/
│   ├── processed/      # persons / competitions / results / reference tables / frozen_stats.json
│   ├── splits/         # train_ids / val_ids / test_ids / person_history / test_time_slices.json
│   └── optional/       # result_attempts.parquet, scrambles.parquet (large, optional)
└── examples/           # baseline reports + leaderboard
```

## Tasks

| ID | Task | Paradigm | Primary metric |
|----|------|----------|----------------|
| T1 | Result prediction | Regression | MAE / RMSE (log) |
| T2 | Placement prediction | Ranking | Kendall's τ, top-3 overlap |
| T3 | DNF prediction | Binary classification | AUC-PR, MCC |
| T4 | Human-limit estimation | Extreme value | LOO stability |
| T5 | Skill-transfer analysis | Causal inference | identified pairs |

## Usage

```python
from modelscope.msdatasets import MsDataset

ds = MsDataset.load("Maicarons/WCA-Bench", subset_name="results", split="train")
print(ds)
```

## Data Creation Notes

- **Result decoding** depends on the event format: `time` values are hundredths of a
  second (`8653` → 1:26.53), `number` values are raw moves (fewest-moves), and `multi`
  values are the multi-blind composite encoding (`1SSAATTTTT` legacy / `0DDTTTTTMM`
  modern). Special values are `-1` (DNF), `-2` (DNS) and `0` (no result).
- **ao5** averages discard the fastest and slowest of five attempts
  (`formats.trim_fastest_n = formats.trim_slowest_n = 1`).
- **No temporal leakage:** `frozen_stats.json` and `person_event_stats.parquet` are
  computed from the training window only (frozen at 2022-12-31) and must not be recomputed
  during evaluation.

## Attribution

This information is based on competition results owned and maintained by the
World Cube Association, published at https://worldcubeassociation.org/results

## Prohibited Uses

- Gambling, betting, or any form of wagering prediction.
- Discriminatory screening, profiling, or shaming of individual contestants.
- Impersonating official bodies or forging competition results.
- Redistributing individual-level, privacy-sensitive derived data without anonymisation.

## Citation

```bibtex
@misc{wcabench2026,
  title        = {WCA-Bench: A Sports Analytics Benchmark from World Cube Association Competition Data},
  author       = {{WCA-Bench Project}},
  year         = {2026},
  version      = {0.1.0},
  howpublished = {\url{https://github.com/Maicarons/WCA-Bench}}
}
```
