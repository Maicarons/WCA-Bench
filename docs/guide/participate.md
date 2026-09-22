# Join the Leaderboard

WCA-Bench ships a **community leaderboard** so anyone can train their own model,
evaluate it on the frozen test split, and be ranked next to the official
baselines.

> **Why are results self-reported?**
> Some metrics cannot be recomputed from a predictions file alone — human-limit
> estimation (T4) depends on leave-one-out stability and skill-transfer analysis
> (T5) on a causal pipeline. Instead of running participant code on our servers,
> participants evaluate locally and submit the resulting **report JSON**. This
> matches the reproducibility levels defined in
> [Reproducibility Requirements](/evaluation/reproducibility): the main table
> requires **L3 (verifiable)** — raw predictions published and metrics
> independently recomputable.

## 1. Get the data

| Source | Link |
| --- | --- |
| Hugging Face | [Maicarons/WCA-Bench](https://huggingface.co/datasets/Maicarons/WCA-Bench) |
| ModelScope | [Mai2026/WCA-Bench](https://www.modelscope.cn/datasets/Mai2026/WCA-Bench) |

Every row carries its `split` label (`train` / `val` / `test`); the frozen
statistics used for features ship alongside it.

```bash
pip install -e ".[dev,fast,boost]"
```

## 2. Train and evaluate

Fit on `train`, select on `val`, and predict on `test` — **never** let test
labels leak into fitting or tuning.

```python
import json
from pathlib import Path

from wca_bench.data.loader import load_dataset
from wca_bench.tasks.result_prediction import ResultPredictionTask

data = load_dataset(raw_dir="data/raw", processed_dir="data/processed", build=True)
task = ResultPredictionTask(data)
splits = task.split()          # {"train": ..., "val": ..., "test": ...}

predictions = my_predict(task, splits["test"])   # your model goes here

report = task.evaluate("my_model", predictions)
Path("result_prediction__my_model.json").write_text(
    json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
)
```

Switch tasks by importing the matching class:

| Task | Class |
| --- | --- |
| `result_prediction` | `wca_bench.tasks.result_prediction.ResultPredictionTask` |
| `placement` | `wca_bench.tasks.placement.PlacementTask` |
| `dnf` | `wca_bench.tasks.dnf.DNFTask` |
| `limit` | `wca_bench.tasks.limit.HumanLimitTask` |
| `transfer` | `wca_bench.tasks.transfer.SkillTransferTask` |

## 3. Submit

Upload the report on the **Submit** tab of the leaderboard Space, or open a pull
request adding it under `community-submissions/`. Every submission is
machine-validated first:

```bash
python scripts/validate_community_submission.py community-submissions
```

The accepted schema is documented in
[community-submissions/README.md](https://github.com/Maicarons/WCA-Bench/blob/main/community-submissions/README.md)
and enforced in CI for every pull request.

## 4. Publish accepted entries

```bash
python scripts/build_leaderboard.py \
  --report-dir examples \
  --with-community \
  --out-dir examples
```

This merges community reports with the offline baselines and rewrites
`examples/leaderboard.{csv,json,md}`; re-publishing the dataset makes the new
table live.

## Rules at a glance

1. Frozen protocol: fit on `train`, select on `val`, report on `test`.
2. Publish training code, seeds, and compute cost (`cost`).
3. Publish raw predictions (L3) so others can recompute your metrics.
4. One entry per `(task, model)`; re-submitting the same name updates that row.
5. Maintainers review suspicious entries (for example `mae_log <= 0`).
