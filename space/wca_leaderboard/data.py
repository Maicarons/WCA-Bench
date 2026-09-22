"""Loader for the official leaderboard table."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import HF_DATASET_REPO, LEADERBOARD_FILENAME

LOCAL_SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "leaderboard.csv"

EXPECTED_COLUMNS = [
    "task",
    "model",
    "primary_metric",
    "primary_value",
    "direction",
    "n",
    "failed",
    "error",
    "_rank",
]

DISPLAY_HEADERS = ["#", "Model", "Task", "Primary metric", "Value", "N"]


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure every expected column exists so downstream code can trust them."""
    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            df[column] = None
    if len(df) and df["_rank"].isna().all():
        df["_rank"] = None
    return df


def _stamp(path: str | Path | None) -> str:
    if path is None:
        return "unknown"
    try:
        mtime = datetime.fromtimestamp(Path(path).stat().st_mtime, tz=timezone.utc)
        return mtime.strftime("%Y-%m-%d %H:%M UTC")
    except OSError:
        return "unknown"


def load_leaderboard(refresh: bool = False) -> tuple[pd.DataFrame, dict[str, str]]:
    """Return ``(frame, meta)``.

    The leaderboard is read from the official dataset repository. A local
    snapshot under ``space/data/leaderboard.csv`` is used as a fallback so the
    Space still renders when the Hub is unreachable.
    """
    notes: list[str] = []

    try:
        from huggingface_hub import hf_hub_download

        path = hf_hub_download(
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            filename=LEADERBOARD_FILENAME,
            force_download=refresh,
        )
        frame = _normalise(pd.read_csv(path))
        if len(frame):
            meta = {
                "source": f"{HF_DATASET_REPO} · {LEADERBOARD_FILENAME}",
                "loaded_at": _stamp(path),
                "note": " ".join(notes),
            }
            return frame, meta
        notes.append("Remote leaderboard is empty; falling back to the local snapshot.")
    except Exception as exc:  # noqa: BLE001 - network / Hub availability
        notes.append(f"Could not read the Hub copy ({exc.__class__.__name__}); "
                     "falling back to the local snapshot.")

    if LOCAL_SNAPSHOT.is_file():
        frame = _normalise(pd.read_csv(LOCAL_SNAPSHOT))
        return frame, {
            "source": "local snapshot · space/data/leaderboard.csv",
            "loaded_at": _stamp(LOCAL_SNAPSHOT),
            "note": " ".join(notes),
        }

    raise RuntimeError(
        "No leaderboard data available: neither the dataset repository nor the "
        "local snapshot could be read."
    )


def _format_value(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "-" if value is None else str(value)
    if not math.isfinite(number):
        return "-"
    if abs(number) >= 1e6:
        return f"{number:.4g}"
    return f"{number:.6g}"


def _format_rank(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "-"
    return str(int(number)) if math.isfinite(number) else "-"


def _format_n(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "-"
    if not math.isfinite(number):
        return "-"
    return str(int(number))


def to_rows(frame: pd.DataFrame, task: str = "all", search: str = "") -> list[list[str]]:
    """Render rows for display, optionally filtered by task / model substring."""
    data = frame.copy()
    if task and task != "all":
        data = data[data["task"] == task]
    needle = (search or "").strip().lower()
    if needle:
        data = data[data["model"].astype(str).str.lower().str.contains(needle, na=False)]

    ordering = pd.to_numeric(data["_rank"], errors="coerce").fillna(float("inf"))
    data = data.assign(_order=ordering).sort_values(["task", "_order"], kind="mergesort")

    rows: list[list[str]] = []
    for _, row in data.iterrows():
        rows.append(
            [
                _format_rank(row["_rank"]),
                str(row["model"]),
                str(row["task"]),
                str(row["primary_metric"]),
                _format_value(row["primary_value"]),
                _format_n(row["n"]),
            ]
        )
    return rows



