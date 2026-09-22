#!/usr/bin/env python
"""Aggregate baseline metrics across multiple random seeds (mean ± std)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))

import run_all_baselines as rab  # noqa: E402
from wca_bench.leaderboard.builder import PRIMARY_METRICS  # noqa: E402
from wca_bench.tasks import TASK_REGISTRY  # noqa: E402
from wca_bench.utils.io import save_json  # noqa: E402


def _finite(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if np.isfinite(out) else None


def aggregate(per_seed_payloads: list[list[dict]], primary_metrics: dict) -> list[dict]:
    """Aggregate primary metric values per (task, model) across seeds."""
    buckets: dict[tuple[str, str], list[float]] = {}
    for payloads in per_seed_payloads:
        for payload in payloads:
            task = payload.get("task")
            model = payload.get("model")
            metric = primary_metrics.get(task, ("", ""))[0]
            val = _finite(payload.get("overall", {}).get(metric))
            if val is None:
                continue
            buckets.setdefault((task, model), []).append(val)

    rows = []
    for (task, model), values in sorted(buckets.items()):
        arr = np.asarray(values, dtype=float)
        rows.append(
            {
                "task": task,
                "model": model,
                "metric": primary_metrics.get(task, ("", ""))[0],
                "mean": float(arr.mean()),
                "std": float(arr.std(ddof=0)),
                "n_seeds": int(len(arr)),
                "values": [float(v) for v in arr],
            }
        )
    return rows


def render_markdown(rows: list[dict], seeds: list[int], mode: str) -> str:
    lines = [
        "# WCA-Bench 多种子结果",
        "",
        f"- 模式：`{mode}`；随机种子：{', '.join(str(s) for s in seeds)}",
        f"- 聚合方式：主指标在 {len(seeds)} 个种子上的均值 ± 标准差",
        "",
    ]
    by_task: dict[str, list[dict]] = {}
    for row in rows:
        by_task.setdefault(row["task"], []).append(row)
    for task, group in by_task.items():
        lines.append(f"## {task}")
        lines.append("")
        lines.append("| model | metric | mean ± std | n_seeds |")
        lines.append("| --- | --- | --- | --- |")
        for row in sorted(group, key=lambda r: r["mean"], reverse=True):
            lines.append(
                f"| {row['model']} | {row['metric']} | {row['mean']:.4f} ± {row['std']:.4f} | {row['n_seeds']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--mode", choices=["small", "full"], default="small")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    parser.add_argument("--tasks", nargs="*", default=list(TASK_REGISTRY.keys()))
    parser.add_argument("--out-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--examples-dir", type=Path, default=ROOT / "examples")
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.examples_dir.mkdir(parents=True, exist_ok=True)

    per_seed_payloads: list[list[dict]] = []
    for seed in args.seeds:
        print(f"--- seed {seed} ---", flush=True)
        data = rab.prepare_data(args.mode, seed)
        per_seed_payloads.append(
            rab.run_task_reports(data, args.tasks, args.mode, seed=seed, device=args.device)
        )

    rows = aggregate(per_seed_payloads, PRIMARY_METRICS)
    payload = {
        "mode": args.mode,
        "seeds": list(args.seeds),
        "tasks": list(args.tasks),
        "results": rows,
    }
    out_json = args.out_dir / "multi_seed.json"
    save_json(payload, out_json)

    md_path = args.examples_dir / "multi_seed.md"
    md_path.write_text(render_markdown(rows, list(args.seeds), args.mode), encoding="utf-8")
    print(f"Wrote {out_json} and {md_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
