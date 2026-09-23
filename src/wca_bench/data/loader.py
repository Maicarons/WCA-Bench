"""Dataset loading: raw WCA TSV or synthetic tables → processed artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from wca_bench.data.features import build_competition_features, build_result_features
from wca_bench.data.reconciliation import (
    compute_average_agreement,
    compute_checksums,
)
from wca_bench.data.splits import assign_split, freeze_stats, time_slice
from wca_bench.utils.io import load_json, read_table, save_json, save_table
from wca_bench.utils.logging import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[3]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_SPLITS = ROOT / "data" / "splits"


@dataclass
class WCABenchData:
    persons: pd.DataFrame
    competitions: pd.DataFrame
    results: pd.DataFrame
    result_attempts: pd.DataFrame
    events: pd.DataFrame
    formats: pd.DataFrame
    round_types: pd.DataFrame
    countries: pd.DataFrame
    continents: pd.DataFrame
    frozen_stats: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "n_persons": int(len(self.persons)),
            "n_competitions": int(len(self.competitions)),
            "n_results": int(len(self.results)),
            "n_attempts": int(len(self.result_attempts)),
            "n_events": int(self.results["event_id"].nunique()) if len(self.results) else 0,
            "n_frozen_person_event": len(self.frozen_stats.get("person_event_stats", {})),
        }


def _read_export_table(raw_dir: Path, table: str) -> pd.DataFrame:
    camel = {
        "persons": ["Persons", "persons"],
        "competitions": ["Competitions", "competitions"],
        "results": ["Results", "results"],
        "result_attempts": ["result_attempts", "ResultAttempts"],
        "scrambles": ["Scrambles", "scrambles"],
        "events": ["Events", "events"],
        "formats": ["Formats", "formats"],
        "round_types": ["round_types", "RoundTypes"],
        "countries": ["Countries", "countries"],
        "continents": ["Continents", "continents"],
        "championships": ["championships", "Championships"],
        "eligible_country_iso2s_for_championship": [
            "eligible_country_iso2s_for_championship",
            "EligibleCountryIso2sForChampionship",
        ],
    }
    names = camel.get(table, [table])
    candidates: list[Path] = []
    for name in names:
        for ext in (".tsv", ".csv", ".parquet"):
            candidates.append(raw_dir / f"WCA_export_{name}{ext}")
            candidates.append(raw_dir / f"{name}{ext}")
    # unique existing files only; prefer larger files (skip stub/header-only exports)
    existing = []
    seen = set()
    for path in candidates:
        key = str(path).lower()
        if key in seen or not path.exists():
            continue
        seen.add(key)
        if path.is_file() and path.stat().st_size > 0:
            existing.append(path)
    if not existing:
        # case-insensitive fallback
        for path in sorted(raw_dir.glob("WCA_export_*")):
            if path.suffix.lower() not in {".tsv", ".csv", ".parquet"}:
                continue
            low = path.name.lower()
            if any(n.lower() in low for n in names):
                existing.append(path)
    if not existing:
        raise FileNotFoundError(f"Cannot find export table '{table}' in {raw_dir}")

    # prefer snake_case / larger files to avoid tiny camelCase stubs
    existing.sort(key=lambda p: (-p.stat().st_size, p.name))
    path = existing[0]
    if path.suffix == ".tsv":
        return pd.read_csv(path, sep="\t")
    return read_table(path)


def _normalize_competitions(competitions: pd.DataFrame) -> pd.DataFrame:
    df = competitions.copy()
    if "start_date" not in df.columns:
        if {"year", "month", "day"}.issubset(df.columns):
            df["start_date"] = pd.to_datetime(
                dict(
                    year=df["year"].fillna(2000).astype(int),
                    month=df["month"].fillna(1).astype(int),
                    day=df["day"].fillna(1).astype(int),
                ),
                errors="coerce",
            ).dt.date
            df.loc[df["start_date"].isna(), "start_date"] = pd.Timestamp("2000-01-01").date()
        else:
            raise ValueError("competitions missing start_date / year-month-day")
    else:
        df["start_date"] = pd.to_datetime(df["start_date"]).dt.date
    return df


def _normalize_results(results: pd.DataFrame, competitions: pd.DataFrame) -> pd.DataFrame:
    df = results.copy()
    # real WCA export uses person_country_id; normalize to country_id
    if "country_id" not in df.columns and "person_country_id" in df.columns:
        df["country_id"] = df["person_country_id"]
    if "start_date" not in df.columns:
        if "competition_id" not in df.columns:
            raise ValueError("results missing competition_id")
        comp_dates = _normalize_competitions(competitions)[["id", "start_date"]].rename(
            columns={"id": "competition_id"}
        )
        df = df.merge(comp_dates, on="competition_id", how="left")
    df["date"] = pd.to_datetime(df["start_date"]).dt.date
    df["split"] = assign_split(df["date"]).values
    df["time_slice"] = time_slice(df["date"]).values
    return df


def load_raw_export(raw_dir: str | Path = DATA_RAW) -> dict[str, pd.DataFrame]:
    raw_dir = Path(raw_dir)
    tables = {}
    required = [
        "persons",
        "competitions",
        "results",
        "result_attempts",
        "events",
        "formats",
        "round_types",
        "countries",
        "continents",
    ]
    optional = ["scrambles", "championships"]
    for table in required:
        tables[table] = _read_export_table(raw_dir, table)
    for table in optional:
        try:
            tables[table] = _read_export_table(raw_dir, table)
        except FileNotFoundError:
            tables[table] = pd.DataFrame()
    return tables


def load_dataset(
    raw_dir: str | Path = DATA_RAW,
    processed_dir: str | Path = DATA_PROCESSED,
    *,
    build: bool = True,
    as_of=None,
) -> WCABenchData:
    """Load processed dataset, building it from raw export when needed."""
    processed_dir = Path(processed_dir)
    marker = processed_dir / "manifest.json"
    if marker.exists() and not build:
        pass
    elif build and (marker.exists() is False or build):
        if not (processed_dir / "results.parquet").exists() and not (
            processed_dir / "results.csv"
        ).exists():
            build_dataset(raw_dir=raw_dir, processed_dir=processed_dir)

    def _load(name: str) -> pd.DataFrame:
        for ext in (".parquet", ".csv"):
            p = processed_dir / f"{name}{ext}"
            if p.exists():
                return read_table(p)
        return pd.DataFrame()

    frozen_path = processed_dir / "frozen_stats.json"
    frozen = load_json(frozen_path) if frozen_path.exists() else {}
    # hydrate person_event_stats from parquet when path marker present
    pe_path = frozen.get("person_event_stats_path")
    if pe_path and Path(pe_path).exists():
        pe_df = read_table(pe_path)
        frozen["person_event_stats"] = {
            (str(r.person_id), str(r.event_id)): {
                "mean_best": r.mean_best,
                "std_best": r.std_best,
                "n_attempts": r.n_attempts,
                "best": r.best,
                "dnf_rate": r.dnf_rate,
            }
            for r in pe_df.itertuples(index=False)
        }
    else:
        pe_local = processed_dir / "person_event_stats.parquet"
        if pe_local.exists():
            pe_df = read_table(pe_local)
            frozen["person_event_stats"] = {
                (str(r.person_id), str(r.event_id)): {
                    "mean_best": r.mean_best,
                    "std_best": r.std_best,
                    "n_attempts": r.n_attempts,
                    "best": r.best,
                    "dnf_rate": r.dnf_rate,
                }
                for r in pe_df.itertuples(index=False)
            }
        else:
            frozen.setdefault("person_event_stats", {})
    return WCABenchData(
        persons=_load("persons"),
        competitions=_load("competitions"),
        results=_load("results"),
        result_attempts=_load("result_attempts"),
        events=_load("events"),
        formats=_load("formats"),
        round_types=_load("round_types"),
        countries=_load("countries"),
        continents=_load("continents"),
        frozen_stats=frozen,
    )


def build_dataset(
    raw_dir: str | Path = DATA_RAW,
    processed_dir: str | Path = DATA_PROCESSED,
    splits_dir: str | Path = DATA_SPLITS,
) -> dict[str, Any]:
    """Stage 1–7 pipeline: validate, decode context, split, freeze stats, export."""
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    splits_dir = Path(splits_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    splits_dir.mkdir(parents=True, exist_ok=True)

    tables = load_raw_export(raw_dir)
    tables["competitions"] = _normalize_competitions(tables["competitions"])
    results = _normalize_results(tables["results"], tables["competitions"])

    # attach person continent if available
    persons = tables["persons"].copy()
    countries = tables.get("countries", pd.DataFrame())
    if not countries.empty:
        # countries.id may be a name (official export); continent_id like _Asia
        cols = [c for c in ["id", "continent_id", "iso2", "name"] if c in countries.columns]
        persons = persons.merge(
            countries[cols],
            left_on="country_id",
            right_on="id",
            how="left",
            suffixes=("", "_country"),
        )
        if "continent_id_country" in persons.columns:
            persons["continent_id"] = persons["continent_id_country"]
    if "continent_id" not in persons.columns:
        persons["continent_id"] = "UNKNOWN"

    frozen = freeze_stats(results, persons)

    # person-event stats stored as parquet for scale; metadata stays JSON
    pe_rows = []
    for k, v in frozen.get("person_event_stats", {}).items():
        if isinstance(k, str) and "::" in k:
            pid, eid = k.split("::", 1)
        elif isinstance(k, (tuple, list)):
            pid, eid = str(k[0]), str(k[1])
        else:
            continue
        pe_rows.append(
            {
                "person_id": pid,
                "event_id": eid,
                "mean_best": v.get("mean_best"),
                "std_best": v.get("std_best"),
                "n_attempts": v.get("n_attempts"),
                "best": v.get("best"),
                "dnf_rate": v.get("dnf_rate"),
            }
        )
    pe_df = pd.DataFrame(pe_rows)
    pe_path = save_table(pe_df, processed_dir / "person_event_stats.parquet")
    save_table(pe_df, splits_dir / "person_event_stats.parquet")

    frozen_json = {
        "frozen_at": frozen.get("frozen_at"),
        "person_event_stats_path": str(pe_path),
        "n_person_event": int(len(pe_df)),
        "world_records": {str(k): v for k, v in (frozen.get("world_records") or {}).items()},
        "skill_thresholds": {
            str(k): {str(kk): float(vv) for kk, vv in v.items()}
            for k, v in (frozen.get("skill_thresholds") or {}).items()
        },
        "continent_map": {str(k): str(v) for k, v in (frozen.get("continent_map") or {}).items()},
        "global_dnf_rate": frozen.get("global_dnf_rate"),
        "n_train_rows": frozen.get("n_train_rows"),
        "slices": frozen.get("slices", {}),
    }
    # keep a small in-memory map for baselines that need frequent lookups
    # load path marker only; loader will hydrate from parquet
    save_json(frozen_json, processed_dir / "frozen_stats.json")
    save_json(frozen_json, splits_dir / "frozen_stats.json")

    # splits
    train_ids = results.loc[results["split"] == "train", "id"] if "id" in results.columns else pd.Series(dtype=int)
    val_ids = results.loc[results["split"] == "val", "id"] if "id" in results.columns else pd.Series(dtype=int)
    test_ids = results.loc[results["split"] == "test", "id"] if "id" in results.columns else pd.Series(dtype=int)
    if "id" not in results.columns:
        results = results.reset_index().rename(columns={"index": "id"})
        train_ids = results.loc[results["split"] == "train", "id"]
        val_ids = results.loc[results["split"] == "val", "id"]
        test_ids = results.loc[results["split"] == "test", "id"]

    save_table(train_ids.to_frame("id"), splits_dir / "train_ids.parquet")
    save_table(val_ids.to_frame("id"), splits_dir / "val_ids.parquet")
    save_table(test_ids.to_frame("id"), splits_dir / "test_ids.parquet")
    save_json(
        {
            "train": frozen["slices"]["train"],
            "val": frozen["slices"]["val"],
            "test": frozen["slices"]["test"],
            "test_a": frozen["slices"]["test_a"],
            "test_b": frozen["slices"]["test_b"],
            "test_c": frozen["slices"]["test_c"],
        },
        splits_dir / "test_time_slices.json",
    )

    # person history sequences
    hist = results.sort_values(["person_id", "date"])[
        ["person_id", "event_id", "competition_id", "date", "best", "average", "split", "time_slice"]
    ]
    save_table(hist, splits_dir / "person_history.parquet")

    # export processed tables
    outputs = {}
    for name, df in {
        "persons": persons,
        "competitions": tables["competitions"],
        "results": results,
        "result_attempts": tables["result_attempts"],
        "events": tables["events"],
        "formats": tables["formats"],
        "round_types": tables["round_types"],
        "countries": tables["countries"],
        "continents": tables["continents"],
        "scrambles": tables.get("scrambles", pd.DataFrame()),
        "championships": tables.get("championships", pd.DataFrame()),
    }.items():
        outputs[name] = str(save_table(df, processed_dir / f"{name}.parquet"))

    # reconciliation
    n_train, n_val, n_test = len(train_ids), len(val_ids), len(test_ids)
    n_total = len(results)
    agreement = compute_average_agreement(results, tables.get("result_attempts", pd.DataFrame()))
    reconciliation = {
        "n_results": n_total,
        "n_train": n_train,
        "n_val": n_val,
        "n_test": n_test,
        "n_assigned": n_train + n_val + n_test,
        "n_out_of_window": int((results["split"] == "out_of_window").sum()),
        "balance_ok": n_train + n_val + n_test + int((results["split"] == "out_of_window").sum())
        == n_total,
        "average_agreement": round(float(agreement["agreement"]), 6),
        "average_agreement_n": int(agreement["n_compared"]),
        "average_agreement_match": int(agreement["n_match"]),
    }

    # content checksums for reproducible builds (A1.2)
    checksums = compute_checksums(outputs)

    manifest = {
        "tables": outputs,
        "checksums": checksums,
        "reconciliation": reconciliation,
        "frozen_at": frozen["frozen_at"],
        "global_dnf_rate": frozen["global_dnf_rate"],
        "raw_dir": str(raw_dir),
    }
    save_json(manifest, processed_dir / "manifest.json")
    save_json(reconciliation, processed_dir / "reconciliation.json")

    # sample feature build for train as_of end of train window
    from datetime import date as date_cls

    as_of = date_cls.fromisoformat(frozen["frozen_at"]) + pd.Timedelta(days=1)
    as_of = as_of.date() if hasattr(as_of, "date") else as_of
    # smaller feature extract for all results using as_of after last date of each split at runtime
    logger.info("Dataset built: %s", reconciliation)
    return manifest


def build_features_for_as_of(
    data: WCABenchData,
    as_of,
    split: str | None = "test",
) -> pd.DataFrame:
    """Convenience wrapper used by tasks/baselines."""
    df = data.results
    if split is not None and len(df):
        df = df[df["split"] == split]
    feats = build_result_features(df, data.frozen_stats, as_of=as_of)
    feats = build_competition_features(feats, data.frozen_stats)
    return feats
