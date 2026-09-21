#!/usr/bin/env python
"""Run all task baselines on the processed dataset and write report/*.json."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd  # noqa: F401

from wca_bench.data.loader import load_dataset  # noqa: E402
from wca_bench.data.splits import time_slice  # noqa: E402
from wca_bench.tasks import TASK_REGISTRY  # noqa: E402
from wca_bench.utils.io import save_json  # noqa: E402
from wca_bench.utils.seed import set_seed  # noqa: E402


def sample_test_results(data, mode: str):
    """Sample test competitions for tractable baseline runs on full WCA export."""
    results = data.results
    test = results[results["split"] == "test"] if len(results) else results
    if test.empty:
        return data
    if "competition_id" not in test.columns:
        return data
    comps = test["competition_id"].drop_duplicates()
    rng = np.random.default_rng(42)
    n = 8 if mode == "small" else 40
    if len(comps) <= n:
        chosen = comps.tolist()
    else:
        chosen = rng.choice(comps.to_numpy(), size=n, replace=False).tolist()
    sampled = test[test["competition_id"].isin(chosen)].copy()
    # keep train slice for training baselines
    train = results[results["split"] == "train"]
    # subsample train for speed while keeping representative coverage
    if len(train) > 400_000:
        train = train.sample(n=400_000, random_state=42)
    val = results[results["split"] == "val"]
    if len(val) > 100_000:
        val = val.sample(n=100_000, random_state=42)
    merged = pd.concat([train, val, sampled], ignore_index=True)
    data.results = merged
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["small", "full"], default="small")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "outputs" / "reports")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tasks", nargs="*", default=list(TASK_REGISTRY.keys()))
    args = parser.parse_args(argv)

    set_seed(args.seed)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    print("Loading processed dataset...", flush=True)
    data = load_dataset(build=False)
    print("dataset:", data.summary(), flush=True)
    data = sample_test_results(data, args.mode)
    print("sampled dataset:", data.summary(), flush=True)
    if "date" not in data.results.columns and "start_date" in data.results.columns:
        data.results["date"] = pd.to_datetime(data.results["start_date"]).dt.date
    if "time_slice" not in data.results.columns:
        data.results["time_slice"] = time_slice(data.results["date"]).values

    max_comps = 3 if args.mode == "small" else 20
    all_reports = []
    for task_name in args.tasks:
        if task_name not in TASK_REGISTRY:
            print(f"skip unknown task {task_name}", flush=True)
            continue
        cls = TASK_REGISTRY[task_name]
        print(f"=== {task_name} ===", flush=True)
        task = cls(data, max_test_competitions=max_comps)
        t0 = time.time()
        reports = task.run_all_baselines(mode=args.mode)
        elapsed = time.time() - t0
        for rep in reports:
            payload = rep.to_dict()
            payload["elapsed_sec"] = elapsed
            payload["seed"] = args.seed
            payload["data_summary"] = data.summary()
            fname = f"{task_name}__{rep.model}.json"
            save_json(payload, args.report_dir / fname)
            all_reports.append(payload)
            status = "FAIL" if payload.get("extras", {}).get("failed") else "OK"
            overall = rep.overall
            # compact print
            keys = [k for k in ["mae_log", "rmse_log", "kendall_tau", "auc_pr", "auc_roc", "mcc", "n", "error"] if k in overall]
            compact = {k: overall[k] for k in keys}
            print(f"[{status}] {task_name}/{rep.model}: {compact}", flush=True)
    save_json(all_reports, args.report_dir / "_all.json")
    print(f"Wrote {len(all_reports)} reports -> {args.report_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
