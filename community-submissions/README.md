# Community Submissions

This directory collects leaderboard entries submitted by the community. Every
file is a single **report JSON** produced by a participant, and every entry is
reviewed by a maintainer before it goes live.

## File layout

```
community-submissions/
└── <task>__<model>.json      # e.g. result_prediction__my_cool_model.json
```

`task` must be one of `result_prediction`, `placement`, `dnf`, `limit`,
`transfer`, and `model` must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`.
The filename convention matches the offline reports in `examples/`; the builder
itself keys off the `task` and `model` fields inside the JSON.

## Minimal report shape

```json
{
  "task": "result_prediction",
  "model": "my_cool_model",
  "overall": {
    "mae_log": 0.1512,
    "rmse_log": 0.4011,
    "n": 2196
  },
  "stratified": {"by_event": {}, "by_skill_level": {}, "by_time_slice": {}, "by_continent": {}},
  "cost": {"device": "cuda:RTX4060", "wall_clock_sec": 812.4, "cpu_hours": 0.23, "gpu_hours": 0.23},
  "extras": {"n": 2196},
  "_submission": {
    "author": "Jane Doe",
    "affiliation": "Example Lab",
    "code_url": "https://github.com/...",
    "weights_url": "https://huggingface.co/...",
    "notes": "Trained with the official train split, 3 seeds.",
    "submitted_at": "2026-09-22T12:00:00Z",
    "source": "HF Space submission form"
  }
}
```

The key under `overall` must match the task's primary metric (see
`src/wca_bench/leaderboard/builder.PRIMARY_METRICS`):

| Task | Primary metric | Direction |
| --- | --- | --- |
| `result_prediction` | `mae_log` | lower is better |
| `placement` | `kendall_tau` | higher is better |
| `dnf` | `auc_pr` | higher is better |
| `limit` | `mean_loo_std` | lower is better |
| `transfer` | `n_identified_pairs` | higher is better |

`_submission` is optional metadata written by the Space submission form; the
leaderboard builder ignores unknown keys.

## Producing a report

```python
import json
from pathlib import Path

from wca_bench.data.loader import load_dataset
from wca_bench.tasks.result_prediction import ResultPredictionTask

data = load_dataset(raw_dir="data/raw", processed_dir="data/processed", build=True)
task = ResultPredictionTask(data)
splits = task.split()

predictions = my_predict(task, splits["test"])      # your model goes here
report = task.evaluate("my_cool_model", predictions)

Path("community-submissions/result_prediction__my_cool_model.json").write_text(
    json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
)
```

Switch tasks by importing the matching class:

| Task | Class |
| --- | --- |
| result_prediction | `wca_bench.tasks.result_prediction.ResultPredictionTask` |
| placement | `wca_bench.tasks.placement.PlacementTask` |
| dnf | `wca_bench.tasks.dnf.DNFTask` |
| limit | `wca_bench.tasks.limit.HumanLimitTask` |
| transfer | `wca_bench.tasks.transfer.SkillTransferTask` |

## Validation

```bash
# validate everything in this directory
python scripts/validate_community_submission.py community-submissions

# or a single file
python scripts/validate_community_submission.py community-submissions/result_prediction__my_cool_model.json
```

The same check runs in CI for every pull request, and the HF Space runs it
before opening a PR.

## Rebuilding the leaderboard with community entries

```bash
python scripts/build_leaderboard.py \
  --report-dir examples \
  --with-community \
  --out-dir examples
```

This regenerates `examples/leaderboard.{csv,json,md}` ranked per task, with
baselines and community entries merged. Re-publish the dataset afterwards so the
Space picks up the new table.
