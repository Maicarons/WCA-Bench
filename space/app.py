"""WCA-Bench community leaderboard (Hugging Face Space).

Layout
------
Leaderboard     – browse the official table by task, with metric directions.
Submit          – upload a report JSON, validate it, and open a pull request.
Participate     – end-to-end how-to for training and evaluating your own model.
Rules           – what counts as a valid community entry.

The Space never trains anything: participants evaluate locally on the frozen
test split and submit the resulting report. Validation mirrors
``scripts/validate_submission.py`` plus the leaderboard report schema.
"""

from __future__ import annotations

import json

import gradio as gr
from wca_leaderboard import data as lb_data
from wca_leaderboard import submit as lb_submit
from wca_leaderboard.config import (
    COMMUNITY_DIR,
    DATASET_URL,
    MS_DATASET_URL,
    SOURCE_REPO_URL,
    TASKS,
)

_STATE: dict = {"frame": None, "meta": {}}

TASK_CHOICES = [("All tasks", "all")] + [
    (spec["title"], name) for name, spec in TASKS.items()
]


# --------------------------------------------------------------------------- #
# Leaderboard tab
# --------------------------------------------------------------------------- #

def get_leaderboard(refresh: bool = False):
    """Load (and cache) the leaderboard table."""
    if refresh or _STATE["frame"] is None:
        frame, meta = lb_data.load_leaderboard(refresh=refresh)
        _STATE["frame"] = frame
        _STATE["meta"] = meta
    return _STATE["frame"], _STATE["meta"]


def _status_text(meta: dict, entries: int) -> str:
    lines = [
        f"**Source:** `{meta.get('source', 'unknown')}` &nbsp;·&nbsp; "
        f"**Snapshot:** {meta.get('loaded_at', 'unknown')} &nbsp;·&nbsp; "
        f"**Entries:** {entries}"
    ]
    if meta.get("note"):
        lines.append("")
        lines.append(f"> {meta['note']}")
    return "\n".join(lines)


def render_leaderboard(task: str, search: str, refresh: bool):
    """Return ``(status_markdown, rows)`` for the selected filters."""
    try:
        frame, meta = get_leaderboard(refresh=refresh)
    except Exception as exc:  # noqa: BLE001 - surfaced to the user verbatim
        return f"⚠️ Could not load the leaderboard: `{exc}`", []
    return _status_text(meta, len(frame)), lb_data.to_rows(frame, task, search)


def initial_leaderboard():
    try:
        return render_leaderboard("all", "", refresh=False)
    except Exception:  # pragma: no cover - startup robustness
        return "Leaderboard unavailable.", []


METRIC_LEGEND = "\n".join(
    f"| `{name}` | {spec['title']} | `{spec['primary_metric']}` | "
    f"{'↑ higher is better' if spec['direction'] == 'higher' else '↓ lower is better'} | "
    f"{spec['question']} |"
    for name, spec in TASKS.items()
)


# --------------------------------------------------------------------------- #
# Submit tab
# --------------------------------------------------------------------------- #

_SUBMIT_INTRO = f"""
Upload the report JSON produced by `task.evaluate("your_model", predictions)`
(see the **Participate** tab). We validate it and — when the maintainers
configured a `GITHUB_TOKEN` secret — open a pull request that adds it to
`{COMMUNITY_DIR}/`. Otherwise you download the validated file and open the PR
yourself.
"""


def handle_submission(
    report_file,
    task_check: str,
    author: str,
    affiliation: str,
    code_url: str,
    weights_url: str,
    notes: str,
):
    if not report_file:
        return "⚠️ Please upload your `{task}__{model}.json` report file.", gr.update(
            visible=False
        )

    try:
        payload = lb_submit.load_report(report_file)
    except json.JSONDecodeError as exc:
        return f"❌ The uploaded file is not valid JSON: `{exc}`", gr.update(visible=False)
    except Exception as exc:  # noqa: BLE001
        return f"❌ Could not read the uploaded file: `{exc}`", gr.update(visible=False)

    frame, _ = _STATE["frame"], None
    existing = set()
    if frame is not None and len(frame):
        task_in_report = payload.get("task")
        existing = set(
            frame[frame["task"] == task_in_report]["model"].astype(str)
        )

    ok, messages = lb_submit.validate_report(
        payload, task_filter=task_check, existing_models=existing
    )
    checklist = "\n".join(f"- {message}" for message in messages)

    if not ok:
        body = "\n".join(
            [
                "### ❌ Validation failed",
                "Fix the items below and try again.",
                "",
                checklist,
            ]
        )
        return body, gr.update(visible=False)

    task = payload["task"]
    model = payload["model"]

    document = lb_submit.build_submission_document(
        payload,
        {
            "author": author or "",
            "affiliation": affiliation or "",
            "code_url": code_url or "",
            "weights_url": weights_url or "",
            "notes": notes or "",
        },
    )
    filename = lb_submit.submission_filename(task, model)
    staged = lb_submit.stage_submission(document, filename)
    content = staged.read_text(encoding="utf-8")

    pr_url, pr_message = lb_submit.open_pull_request(
        filename=filename,
        content=content,
        task=task,
        model=model,
        author=author or "",
        code_url=code_url or "",
        weights_url=weights_url or "",
        notes=notes or "",
    )

    lines = [
        f"### ✅ Validation passed for `{task}` · `{model}`",
        "",
        checklist,
        "",
        f"**Target path:** `{lb_submit.repo_path_for(filename)}`",
        "",
        pr_message,
    ]
    if pr_url:
        lines.extend(["", f"🔗 [Pull request #{pr_url.rsplit('/', 1)[-1]}]({pr_url})"])
    lines.append(
        "\nA maintainer will review it; once merged and the leaderboard is rebuilt, "
        "your entry appears on the Leaderboard tab."
    )
    return "\n".join(lines), gr.update(value=str(staged), visible=True)


# --------------------------------------------------------------------------- #
# Static copy for the guide / rules tabs
# --------------------------------------------------------------------------- #

_PARTICIPATE = f"""
## How to participate

WCA-Bench evaluates five tasks on the frozen **test split** of the official WCA
export. You train whatever you like — the only requirement is that you never
touch test labels, and that you submit a report everybody can reproduce.

### 1. Get the data

- Hugging Face: [{DATASET_URL}]({DATASET_URL})
- ModelScope mirror: [{MS_DATASET_URL}]({MS_DATASET_URL})

Every row already carries its `split` label (`train` / `val` / `test`), and the
frozen statistics used for features ship alongside it.

```bash
pip install -e ".[dev,fast,boost]"
```

### 2. Train your model

Use the `train` split for fitting and `val` for model selection. The `test`
split is only for producing the final predictions you submit.

### 3. Evaluate with WCA-Bench and dump the report

```python
import json
from pathlib import Path

from wca_bench.data.loader import load_dataset
from wca_bench.tasks.result_prediction import ResultPredictionTask

data = load_dataset(raw_dir="data/raw", processed_dir="data/processed", build=True)
task = ResultPredictionTask(data)
splits = task.split()          # {{"train": ..., "val": ..., "test": ...}}

predictions = my_predict(task, splits["test"])   # <- your model goes here

report = task.evaluate("my_model", predictions)
Path("result_prediction__my_model.json").write_text(
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

The output must be named **`<task>__<model>.json`** — the leaderboard builder
picks up every report in `examples/` and `{COMMUNITY_DIR}/` that carries both a
`task` and a `model` key.

### 4. Submit

Return to the **Submit** tab, upload the JSON, and add your code / weights
links. The report already contains the metrics, so nothing is recomputed here —
make sure your numbers come from the official test split.
"""

_RULES = f"""
## Rules for community entries

1. **Frozen protocol.** Fit on `train`, select on `val`, report on `test`. Any
   use of test labels for training or tuning disqualifies the entry.
2. **Reproducible materials.** Publish training code, seeds, and — for inclusion
   in the main table (L3) — raw predictions so others can recompute your metrics.
   See `docs/evaluation/reproducibility.md`.
3. **Honest reporting.** Report the compute cost (`cost`) so that
   "100× compute for +1%" is visible. Do not cherry-pick seeds or sub-benchmarks.
4. **One entry per model per task.** Re-submitting the same `model` name updates
   the existing row after maintainer review.
5. **Maintainers may verify.** Suspicious entries (e.g. `mae_log <= 0`) are
   flagged automatically and reviewed manually before they go live.

The full protocol lives in the repository:
[{SOURCE_REPO_URL}]({SOURCE_REPO_URL}).
"""


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #

def build_app() -> gr.Blocks:
    with gr.Blocks(title="WCA-Bench Leaderboard", fill_height=True) as demo:
        gr.Markdown(
            f"""
# 🧊 WCA-Bench Leaderboard

Community ranking for **WCA-Bench** — five sports-analytics tasks built on the
official World Cube Association results export (~6.9M results).

Train whatever you like, evaluate on the frozen test split, and submit your
report through the **Submit** tab. Data:
[{DATASET_URL}]({DATASET_URL}) · [{MS_DATASET_URL}]({MS_DATASET_URL}) ·
[Source]({SOURCE_REPO_URL})
"""
        )

        with gr.Tabs():
            with gr.Tab("🏆 Leaderboard"):
                with gr.Row():
                    task_filter = gr.Dropdown(
                        choices=TASK_CHOICES,
                        value="all",
                        label="Task",
                        scale=2,
                    )
                    search_box = gr.Textbox(
                        value="",
                        label="Filter by model name",
                        placeholder="e.g. xgboost",
                        scale=2,
                    )
                    refresh_btn = gr.Button("🔄 Refresh data", scale=1)
                status_md = gr.Markdown()
                table = gr.Dataframe(
                    headers=lb_data.DISPLAY_HEADERS,
                    value=initial_leaderboard()[1],
                    interactive=False,
                    wrap=False,
                )
                gr.Markdown(
                    "| Task | Description | Primary metric | Direction | Question |\n"
                    "| --- | --- | --- | --- | --- |\n" + METRIC_LEGEND
                )

                for control in (task_filter, search_box):
                    control.change(
                        lambda task, search: render_leaderboard(task, search, False),
                        inputs=[task_filter, search_box],
                        outputs=[status_md, table],
                    )
                refresh_btn.click(
                    lambda task, search: render_leaderboard(task, search, True),
                    inputs=[task_filter, search_box],
                    outputs=[status_md, table],
                )
                demo.load(
                    lambda: render_leaderboard("all", "", False),
                    outputs=[status_md, table],
                )

            with gr.Tab("📤 Submit"):
                gr.Markdown(_SUBMIT_INTRO)
                with gr.Row():
                    report_upload = gr.File(
                        label="Report JSON (task__model.json)",
                        file_types=[".json"],
                        type="filepath",
                    )
                    task_check = gr.Dropdown(
                        choices=TASK_CHOICES,
                        value="all",
                        label="Expected task (cross-check)",
                    )
                with gr.Row():
                    author_box = gr.Textbox(label="Author / team", scale=1)
                    affiliation_box = gr.Textbox(label="Affiliation (optional)", scale=1)
                with gr.Row():
                    code_box = gr.Textbox(label="Training code URL", scale=1)
                    weights_box = gr.Textbox(label="Weights / artifacts URL", scale=1)
                notes_box = gr.Textbox(label="Notes for maintainers", lines=3)
                submit_btn = gr.Button("Validate & submit", variant="primary")
                submit_out = gr.Markdown()
                download_out = gr.File(label="Validated submission file", visible=False)
                submit_btn.click(
                    handle_submission,
                    inputs=[
                        report_upload,
                        task_check,
                        author_box,
                        affiliation_box,
                        code_box,
                        weights_box,
                        notes_box,
                    ],
                    outputs=[submit_out, download_out],
                )

            with gr.Tab("🚀 Participate"):
                gr.Markdown(_PARTICIPATE)

            with gr.Tab("📜 Rules"):
                gr.Markdown(_RULES)

    return demo


if __name__ == "__main__":
    build_app().queue().launch()
