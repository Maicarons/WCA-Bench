"""Integration: synthetic end-to-end pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from wca_bench.data.loader import build_dataset
from wca_bench.data.synthetic import SyntheticConfig, generate_synthetic_dataset
from wca_bench.tasks import TASK_REGISTRY


def test_synthetic_e2e(tmp_path):
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    splits = tmp_path / "splits"
    generate_synthetic_dataset(raw, SyntheticConfig(n_persons=60, n_competitions=18, seed=7), small=False)
    manifest = build_dataset(raw_dir=raw, processed_dir=processed, splits_dir=splits)
    assert manifest["reconciliation"]["n_results"] > 0
    assert manifest["reconciliation"]["balance_ok"]

    from wca_bench.data.loader import WCABenchData
    from wca_bench.utils.io import load_json, read_table

    frozen = load_json(processed / "frozen_stats.json")
    data = WCABenchData(
        persons=read_table(processed / "persons.parquet"),
        competitions=read_table(processed / "competitions.parquet"),
        results=read_table(processed / "results.parquet"),
        result_attempts=read_table(processed / "result_attempts.parquet"),
        events=read_table(processed / "events.parquet"),
        formats=read_table(processed / "formats.parquet"),
        round_types=read_table(processed / "round_types.parquet"),
        countries=read_table(processed / "countries.parquet"),
        continents=read_table(processed / "continents.parquet"),
        frozen_stats=frozen,
    )
    assert len(data.results) > 0
    assert (data.results["split"] == "train").any()
    assert (data.results["split"] == "test").any()

    for name, cls in TASK_REGISTRY.items():
        task = cls(data, max_test_competitions=2)
        reports = task.run_all_baselines(mode="small")
        assert isinstance(reports, list)
        assert len(reports) >= 2
        # at least one report should not hard-fail for core tasks
        if name in {"result_prediction", "dnf"}:
            ok = [r for r in reports if not r.extras.get("failed")]
            assert ok, [r.overall for r in reports]
