#!/usr/bin/env python
"""Validate community leaderboard submissions.

Each submission is a single **report JSON** living in ``community-submissions/``.
This script checks it against the leaderboard report schema:

* the report is a JSON object carrying ``task`` and ``model``;
* the task is one of the five benchmark tasks;
* the model name is filesystem- and leaderboard-safe;
* ``overall`` contains the task's primary metric as a finite number;
* the run is not reported as failed / errored.

It deliberately depends only on the standard library so CI can run it without
installing the full project.

Examples
--------
Validate a whole directory::

    python scripts/validate_community_submission.py community-submissions

Validate specific files::

    python scripts/validate_community_submission.py community-submissions/foo__bar.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

# Mirrors src/wca_bench/leaderboard/builder.PRIMARY_METRICS. Keep in sync.
PRIMARY_METRICS: dict[str, tuple[str, str]] = {
    "result_prediction": ("mae_log", "lower"),
    "placement": ("kendall_tau", "higher"),
    "dnf": ("auc_pr", "higher"),
    "limit": ("mean_loo_std", "lower"),
    "transfer": ("n_identified_pairs", "higher"),
}

NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def validate_report(payload: object) -> tuple[bool, list[str]]:
    """Return ``(ok, messages)`` for one community report."""
    ok = True
    messages: list[str] = []

    def check(condition: bool, label: str) -> None:
        nonlocal ok
        messages.append(("[PASS] " if condition else "[FAIL] ") + label)
        if not condition:
            ok = False

    def warn(condition: bool, label: str) -> None:
        if not condition:
            messages.append("[WARN] " + label)

    check(isinstance(payload, dict), "report is a JSON object")
    if not isinstance(payload, dict):
        return ok, messages

    task = payload.get("task")
    check(task in PRIMARY_METRICS, f"task is one of {sorted(PRIMARY_METRICS)} (got {task!r})")
    if task not in PRIMARY_METRICS:
        return ok, messages

    model = payload.get("model")
    check(isinstance(model, str) and bool(model.strip()), "model name is a non-empty string")
    check(
        isinstance(model, str) and bool(NAME_PATTERN.match(model or "")),
        "model name matches ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$",
    )

    overall = payload.get("overall")
    check(isinstance(overall, dict) and len(overall) > 0, "overall metrics object is present")

    metric, _direction = PRIMARY_METRICS[task]
    value = overall.get(metric) if isinstance(overall, dict) else None
    numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
    check(
        numeric and math.isfinite(float(value)),
        f"primary metric '{metric}' is a finite number (got {value!r})",
    )
    if numeric and math.isfinite(float(value)):
        check(
            (task == "placement" and -1.0 <= float(value) <= 1.0) or task != "placement",
            f"'{metric}' lies in a plausible range",
        )
        warn(
            not (task == "result_prediction" and float(value) <= 0),
            f"'{metric}' <= 0 looks implausible; double-check the split",
        )

    warn("n" in (overall or {}) or "extras" in payload, "sample size `n` is reported")
    warn(isinstance(payload.get("cost"), dict), "cost record present (recommended)")
    warn(isinstance(payload.get("stratified"), dict), "stratified breakdown present (recommended)")

    extras = payload.get("extras") or {}
    if isinstance(extras, dict) and extras.get("failed"):
        check(False, "report is not marked as failed")
    if isinstance(overall, dict) and overall.get("error"):
        check(False, f"report carries no error field (got {overall.get('error')!r})")

    return ok, messages


def _collect(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if target.is_dir():
            files.extend(sorted(p for p in target.glob("*.json") if not p.name.startswith("_")))
        elif target.is_file():
            files.append(target)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate community leaderboard submissions.")
    parser.add_argument(
        "targets",
        nargs="+",
        type=Path,
        help="report JSON files and/or directories containing them",
    )
    args = parser.parse_args(argv)

    files = _collect(args.targets)
    if not files:
        print("[warn] no submission files found; nothing to validate.")
        return 0

    failures = 0
    for path in files:
        print(f"== {path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures += 1
            print(f"  [FAIL] valid JSON: {exc}")
            continue
        ok, messages = validate_report(payload)
        for line in messages:
            print(f"  {line}")
        print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
        if not ok:
            failures += 1

    print()
    print(f"Validated {len(files)} file(s); {failures} failing.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
