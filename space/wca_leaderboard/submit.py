"""Submission validation and (optional) automatic pull-request creation."""

from __future__ import annotations

import base64
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import COMMUNITY_DIR, GITHUB_REPO, TASKS

NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

#: files written by the Space before they are turned into a pull request
STAGING_DIR = Path(__file__).resolve().parents[1] / "_submissions"


def load_report(path: str | Path) -> dict:
    """Read an uploaded report JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_report(payload, *, task_filter: str | None = None,
                    existing_models: set[str] | None = None) -> tuple[bool, list[str]]:
    """Validate a community report against the leaderboard submission spec.

    Returns ``(ok, messages)``. ``ok`` is False if any hard requirement fails.
    """
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

    task = payload.get("task") if isinstance(payload, dict) else None
    check(task in TASKS, f"task is one of {sorted(TASKS)} (got {task!r})")
    if task not in TASKS:
        return ok, messages

    if task_filter and task_filter != "all" and task != task_filter:
        check(False, f"selected task matches the report task (expected {task_filter})")

    model = payload.get("model")
    check(isinstance(model, str) and bool(model.strip()), "model name is a non-empty string")
    check(
        isinstance(model, str) and bool(NAME_PATTERN.match(model or "")),
        "model name matches ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$",
    )
    if existing_models and isinstance(model, str):
        warn(
            model not in existing_models,
            f"model '{model}' already exists on this task's leaderboard — resubmitting "
            "will update that entry only if a maintainer accepts the PR.",
        )

    overall = payload.get("overall")
    check(isinstance(overall, dict) and len(overall) > 0, "overall metrics object is present")
    if isinstance(overall, dict) and task in TASKS:
        metric = TASKS[task]["primary_metric"]
        value = overall.get(metric)
        numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
        check(
            numeric and math.isfinite(float(value)),
            f"primary metric '{metric}' is a finite number (got {value!r})",
        )
        if numeric and task == "result_prediction" and float(value) <= 0:
            warn(False, f"'{metric}' looks suspiciously good (<= 0); please double-check the split.")
        warn("n" in overall or "extras" in payload, "sample size `n` is reported")

    warn(isinstance(payload.get("cost"), dict), "cost record present (recommended for ranking transparency)")
    warn(isinstance(payload.get("stratified"), dict), "stratified breakdown present (recommended)")

    extras = payload.get("extras") or {}
    if isinstance(extras, dict) and extras.get("failed"):
        messages.append("[FAIL] report is marked as failed")
        ok = False

    error = (payload.get("overall") or {}).get("error") if isinstance(payload.get("overall"), dict) else None
    if error:
        messages.append(f"[FAIL] report carries an error field: {error}")
        ok = False

    return ok, messages


def build_submission_document(payload: dict, meta: dict) -> dict:
    """Attach provenance metadata to the report."""
    document = dict(payload)
    document["_submission"] = {
        "author": meta.get("author", ""),
        "affiliation": meta.get("affiliation", ""),
        "code_url": meta.get("code_url", ""),
        "weights_url": meta.get("weights_url", ""),
        "notes": meta.get("notes", ""),
        "submitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "HF Space submission form",
    }
    return document


def submission_filename(task: str, model: str) -> str:
    return f"{task}__{model}.json"


def stage_submission(document: dict, filename: str) -> Path:
    """Write the submission locally so the user can download / PR it manually."""
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = STAGING_DIR / filename
    target.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def repo_path_for(filename: str) -> str:
    return f"{COMMUNITY_DIR}/{filename}"


def open_pull_request(
    *,
    filename: str,
    content: str,
    task: str,
    model: str,
    author: str,
    code_url: str = "",
    weights_url: str = "",
    notes: str = "",
) -> tuple[str | None, str]:
    """Create a PR adding the submission. Returns ``(pr_url, message)``.

    Requires the ``GITHUB_TOKEN`` secret in the Space. When it is missing the
    caller falls back to manual submission instructions.
    """
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("WCA_SUBMISSIONS_REPO", GITHUB_REPO)
    if not token:
        return None, (
            "`GITHUB_TOKEN` is not configured in this Space, so the automatic "
            "pull request is disabled. Download the validated file below and open "
            f"a PR adding it as `{repo_path_for(filename)}`."
        )

    try:
        import requests
    except ImportError:  # pragma: no cover - requests is pinned in requirements
        return None, "`requests` is not installed; cannot create the pull request."

    api = "https://api.github.com"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    branch = "submission/" + _slug(f"{model}-{int(datetime.now().timestamp())}")

    try:
        repo_info = requests.get(f"{api}/repos/{repo}", headers=headers, timeout=30)
        if repo_info.status_code != 200:
            return None, f"GitHub repository lookup failed ({repo_info.status_code}): {repo_info.text[:200]}"
        base = repo_info.json()["default_branch"]

        ref = requests.get(f"{api}/repos/{repo}/git/ref/heads/{base}", headers=headers, timeout=30)
        if ref.status_code != 200:
            return None, f"Could not resolve the base branch ({ref.status_code})."
        sha = ref.json()["object"]["sha"]

        created = requests.post(
            f"{api}/repos/{repo}/git/refs",
            headers=headers,
            json={"ref": f"refs/heads/{branch}", "sha": sha},
            timeout=30,
        )
        if created.status_code not in (200, 201, 422):
            return None, f"Could not create branch {branch} ({created.status_code}): {created.text[:200]}"

        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        put = requests.put(
            f"{api}/repos/{repo}/contents/{repo_path_for(filename)}",
            headers=headers,
            json={
                "message": f"Add community leaderboard submission: {model} ({task})",
                "content": encoded,
                "branch": branch,
            },
            timeout=60,
        )
        if put.status_code not in (200, 201):
            detail = put.json().get("message", put.text[:200]) if put.content else str(put.status_code)
            return None, f"Could not write {repo_path_for(filename)} ({put.status_code}): {detail}"

        body = _pr_body(task, model, author, code_url, weights_url, notes)
        pull = requests.post(
            f"{api}/repos/{repo}/pulls",
            headers=headers,
            json={
                "title": f"[Community Submission] {task} · {model}",
                "head": branch,
                "base": base,
                "body": body,
            },
            timeout=60,
        )
        if pull.status_code not in (200, 201):
            detail = pull.json().get("message", pull.text[:200]) if pull.content else str(pull.status_code)
            return None, f"File committed but the PR could not be opened ({pull.status_code}): {detail}"

        return pull.json()["html_url"], f"Pull request opened against {repo}."
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the user
        return None, f"Unexpected error while contacting GitHub: {exc}"


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower() or "entry"


def _pr_body(task: str, model: str, author: str, code_url: str, weights_url: str, notes: str) -> str:
    lines = [
        f"- **Task**: `{task}`",
        f"- **Model**: `{model}`",
        f"- **Author**: {author or '(not provided)'}",
    ]
    if code_url:
        lines.append(f"- **Training code**: {code_url}")
    if weights_url:
        lines.append(f"- **Weights / reproducibility artifacts**: {weights_url}")
    lines.extend(
        [
            "",
            "Submitted through the WCA-Bench leaderboard Space.",
            "",
            "**Checklist (see `docs/evaluation/reproducibility.md`)**",
            "- [ ] Training code and seeds are public",
            "- [ ] Compute cost reported (`cost`)",
            "- [ ] Predictions are downloadable so metrics can be recomputed (L3)",
        ]
    )
    if notes:
        lines.extend(["", "**Notes**", "", notes])
    return "\n".join(lines)
