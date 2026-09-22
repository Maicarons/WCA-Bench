---
title: WCA-Bench Leaderboard
emoji: 🧊
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: other
license_name: wca-export-terms
license_link: https://www.worldcubeassociation.org/export/results
short_description: Community leaderboard for WCA-Bench
tags:
- benchmark
- leaderboard
- sports-analytics
- tabular
- speedcubing
---

# WCA-Bench Leaderboard

Community ranking for **WCA-Bench**, a sports-analytics benchmark built on the
official World Cube Association results export (~6.9M results, 2003–2026).

## Tasks

| Task | Description | Primary metric | Direction |
| --- | --- | --- | --- |
| `result_prediction` (T1) | Predict a competitor's result | `mae_log` | ↓ lower |
| `placement` (T2) | Rank all competitors of a round | `kendall_tau` | ↑ higher |
| `dnf` (T3) | Predict a DNF attempt | `auc_pr` | ↑ higher |
| `limit` (T4) | Estimate the human performance limit | `mean_loo_std` | ↓ lower |
| `transfer` (T5) | Identify skill-transfer pairs | `n_identified_pairs` | ↑ higher |

## Join the leaderboard

1. Download the dataset (frozen splits + frozen stats) and install `wca_bench`.
2. Fit on `train`, select on `val`, predict on the frozen `test` split.
3. Call `task.evaluate("your_model", predictions)` and save `<task>__<model>.json`.
4. Upload it on the **Submit** tab — validation runs automatically and, when
   configured, opens a pull request adding it to `community-submissions/`.

Full details are in the **Participate** and **Rules** tabs.

## How ranking works

Each task is ranked independently on its primary metric, using the same ranking
logic as the official leaderboard builder
(`src/wca_bench/leaderboard/builder.py`): ties share a rank (average method),
and entries whose metric is missing or whose report failed are listed without a
rank.

## Links

- Dataset: [Maicarons/WCA-Bench](https://huggingface.co/datasets/Maicarons/WCA-Bench)
- ModelScope mirror: [Mai2026/WCA-Bench](https://www.modelscope.cn/datasets/Mai2026/WCA-Bench)
- Source: [github.com/Maicarons/WCA-Bench](https://github.com/Maicarons/WCA-Bench)
