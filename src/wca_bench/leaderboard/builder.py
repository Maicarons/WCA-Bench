"""Leaderboard builders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from wca_bench.utils.io import load_json, save_json

PRIMARY_METRICS = {
    "result_prediction": ("mae_log", "lower"),
    "placement": ("kendall_tau", "higher"),
    "dnf": ("auc_pr", "higher"),
    "limit": ("mean_loo_std", "lower"),
    "transfer": ("n_identified_pairs", "higher"),
}


def collect_reports(report_dir: str | Path) -> list[dict[str, Any]]:
    report_dir = Path(report_dir)
    rows: list[dict[str, Any]] = []
    if not report_dir.exists():
        return rows
    for path in sorted(report_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        data = load_json(path)
        if isinstance(data, dict) and "task" in data and "model" in data:
            rows.append(data)
        elif isinstance(data, list):
            rows.extend([x for x in data if isinstance(x, dict)])
    return rows


def _is_finite(x) -> bool:
    try:
        import numpy as np

        return bool(pd.notna(x) and np.isfinite(float(x)))
    except Exception:
        return pd.notna(x)


def build_leaderboard(report_dir: str | Path) -> pd.DataFrame:
    rows = collect_reports(report_dir)
    flat = []
    for r in rows:
        task = r.get("task", "")
        model = r.get("model", "")
        overall = r.get("overall") or {}
        primary, direction = PRIMARY_METRICS.get(task, ("", "higher"))
        flat.append(
            {
                "task": task,
                "model": model,
                "primary_metric": primary,
                "primary_value": overall.get(primary),
                "direction": direction,
                "n": overall.get("n", r.get("extras", {}).get("n")),
                "failed": bool(r.get("extras", {}).get("failed", False)),
                "error": overall.get("error"),
            }
        )
    df = pd.DataFrame(flat)
    if df.empty:
        return df
    parts = []
    for _, g in df.groupby("task", sort=False):
        g = g.copy()
        vals = pd.to_numeric(g["primary_value"], errors="coerce")
        direction = g["direction"].iloc[0]
        g["_rank"] = vals.rank(ascending=(direction == "lower"))
        parts.append(g.sort_values("_rank"))
    return pd.concat(parts, ignore_index=True)


def write_leaderboard(report_dir: str | Path, out_dir: str | Path) -> dict[str, str]:
    report_dir = Path(report_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = build_leaderboard(report_dir)
    csv_path = out_dir / "leaderboard.csv"
    json_path = out_dir / "leaderboard.json"
    md_path = out_dir / "leaderboard.md"
    if len(df):
        df.to_csv(csv_path, index=False)
        save_json(df.to_dict(orient="records"), json_path)
    else:
        save_json([], json_path)
        csv_path.write_text("task,model,primary_metric,primary_value\n", encoding="utf-8")

    lines = ["# WCA-Bench Leaderboard", ""]
    if len(df):
        for task, g in df.groupby("task"):
            lines.append(f"## {task}")
            lines.append("")
            lines.append("| rank | model | primary | value | n |")
            lines.append("| --- | --- | --- | --- | --- |")
            for _, row in g.sort_values("_rank").iterrows():
                val = row["primary_value"]
                val_s = f"{val:.4f}" if _is_finite(val) else str(val)
                rank = int(row["_rank"]) if _is_finite(row["_rank"]) else "-"
                lines.append(
                    f"| {rank} | {row['model']} | {row['primary_metric']} | {val_s} | {row['n']} |"
                )
            lines.append("")
    else:
        lines.append("_暂无报告，请先运行 `scripts/run_all_baselines.py`。_")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"csv": str(csv_path), "json": str(json_path), "md": str(md_path)}
