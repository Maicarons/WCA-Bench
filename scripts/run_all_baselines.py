#!/usr/bin/env python
"""Run all task baselines on the processed dataset and write report/*.json."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wca_bench.data.loader import DATA_PROCESSED, DATA_RAW, load_dataset  # noqa: E402
from wca_bench.data.splits import time_slice  # noqa: E402
from wca_bench.tasks import TASK_REGISTRY  # noqa: E402
from wca_bench.utils.io import save_json  # noqa: E402
from wca_bench.utils.seed import set_seed  # noqa: E402


def sample_test_results(data, mode: str, seed: int = 42):
    """Sample test competitions for tractable baseline runs on full WCA export."""
    results = data.results
    test = results[results["split"] == "test"] if len(results) else results
    if test.empty:
        return data
    if "competition_id" not in test.columns:
        return data
    comps = test["competition_id"].drop_duplicates()
    rng = np.random.default_rng(seed)
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


def prepare_data(mode: str, seed: int, processed_dir=None, raw_dir=None):
    """Load processed dataset and apply the sampling protocol for the given mode."""
    data = load_dataset(
        raw_dir=raw_dir or DATA_RAW,
        processed_dir=processed_dir or DATA_PROCESSED,
        build=False,
    )
    data = sample_test_results(data, mode, seed=seed)
    if "date" not in data.results.columns and "start_date" in data.results.columns:
        data.results["date"] = pd.to_datetime(data.results["start_date"]).dt.date
    if "time_slice" not in data.results.columns and "date" in data.results.columns:
        data.results["time_slice"] = time_slice(data.results["date"]).values
    return data


def run_task_reports(data, task_names, mode: str, seed: int = 42, device: str = "cpu"):
    """Run the baselines for the requested tasks and return serialised reports."""
    set_seed(seed)
    max_comps = 3 if mode == "small" else 20
    all_reports = []
    for task_name in task_names:
        if task_name not in TASK_REGISTRY:
            print(f"skip unknown task {task_name}", flush=True)
            continue
        cls = TASK_REGISTRY[task_name]
        print(f"=== {task_name} ===", flush=True)
        task = cls(data, max_test_competitions=max_comps)
        task.device = device
        t0 = time.time()
        reports = task.run_all_baselines(mode=mode)
        elapsed = time.time() - t0
        for rep in reports:
            payload = rep.to_dict()
            payload["elapsed_sec"] = elapsed
            payload["seed"] = seed
            payload["data_summary"] = data.summary()
            all_reports.append(payload)
            status = "FAIL" if payload.get("extras", {}).get("failed") else "OK"
            overall = rep.overall
            keys = [
                k
                for k in ["mae_log", "rmse_log", "kendall_tau", "auc_pr", "auc_roc", "mcc", "n", "error"]
                if k in overall
            ]
            compact = {k: overall[k] for k in keys}
            print(f"[{status}] {task_name}/{rep.model}: {compact}", flush=True)
    return all_reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["small", "full"], default="small")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "outputs" / "reports")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    parser.add_argument("--raw-dir", type=Path, default=DATA_RAW)
    parser.add_argument("--processed-dir", type=Path, default=DATA_PROCESSED)
    parser.add_argument("--tasks", nargs="*", default=list(TASK_REGISTRY.keys()))
    args = parser.parse_args(argv)

    args.report_dir.mkdir(parents=True, exist_ok=True)

    print("Loading processed dataset...", flush=True)
    data = prepare_data(args.mode, args.seed, processed_dir=args.processed_dir, raw_dir=args.raw_dir)
    print("sampled dataset:", data.summary(), flush=True)

    all_reports = run_task_reports(data, args.tasks, args.mode, seed=args.seed, device=args.device)
    for payload in all_reports:
        fname = f"{payload['task']}__{payload['model']}.json"
        save_json(payload, args.report_dir / fname)
    save_json(all_reports, args.report_dir / "_all.json")
    print(f"Wrote {len(all_reports)} reports -> {args.report_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
