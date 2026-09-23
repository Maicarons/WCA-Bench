#!/usr/bin/env python3
"""Stage the WCA-Bench release artifacts for Hugging Face Hub / ModelScope upload.

This tool assembles ``data/processed``, ``data/splits`` and ``examples`` into a
single upload-ready directory that follows the layout documented in
``publish/DATASET_LAYOUT.md``. The staging directory is disposable: it can be
regenerated from the repository sources at any time.

Two tiers are supported:

``core`` (default)
    The small reference tables, ``persons``, ``competitions``, ``results``,
    ``person_event_stats``, the frozen statistics and the train/val/test split
    indices. This is what most users need and is ~235 MB.

``full``
    Everything in ``core`` plus the optional large tables ``scrambles`` and
    ``result_attempts`` (staged under ``data/optional/``), ~512 MB total.

Examples
--------
Dry-run the core layout::

    python publish/tools/stage_release.py --tier core --dry-run

Stage the full dataset::

    python publish/tools/stage_release.py --tier full
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

PUBLISH_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PUBLISH_DIR.parent
DEFAULT_SOURCE = REPO_ROOT / "data"
DEFAULT_EXAMPLES = REPO_ROOT / "examples"
DEFAULT_OUT = PUBLISH_DIR / "_staging"
DEFAULT_CARD_DIR = PUBLISH_DIR / "huggingface"

# Files copied from data/processed into <staging>/data/processed/ for the core tier.
PROCESSED_CORE = (
    "persons.parquet",
    "competitions.parquet",
    "results.parquet",
    "person_event_stats.parquet",
    "events.parquet",
    "formats.parquet",
    "round_types.parquet",
    "countries.parquet",
    "continents.parquet",
    "championships.parquet",
    "frozen_stats.json",
    "manifest.json",
    "reconciliation.json",
)

# Large optional tables, staged under <staging>/data/optional/ for the full tier.
PROCESSED_OPTIONAL = (
    "scrambles.parquet",
    "result_attempts.parquet",
)

# Files copied from data/splits into <staging>/data/splits/.
SPLITS_CORE = (
    "train_ids.parquet",
    "val_ids.parquet",
    "test_ids.parquet",
    "person_history.parquet",
    "person_event_stats.parquet",
    "frozen_stats.json",
    "test_time_slices.json",
)

# Card/metadata files copied to the root of the staged dataset.
CARD_FILES = (
    "README.md",
    ".gitattributes",
    "dataset_infos.json",
)

MANIFEST_NAME = "RELEASE_MANIFEST.json"


@dataclass
class StagedFile:
    """A single file that will be copied into the staging directory."""

    src: Path
    rel_dst: str

    @property
    def size(self) -> int:
        return self.src.stat().st_size if self.src.exists() else 0

    @property
    def exists(self) -> bool:
        return self.src.is_file()

    def sha256(self) -> str:
        digest = hashlib.sha256()
        with self.src.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        return digest.hexdigest()


def human_size(num_bytes: int) -> str:
    """Return a short human-readable size string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


def plan_stage(
    tier: str,
    source_dir: Path,
    examples_dir: Path,
    card_dir: Path,
    include_examples: bool,
) -> list[StagedFile]:
    """Return the ordered list of files for the requested tier."""
    files: list[StagedFile] = []

    for name in PROCESSED_CORE:
        files.append(StagedFile(source_dir / "processed" / name, f"data/processed/{name}"))

    if tier == "full":
        for name in PROCESSED_OPTIONAL:
            files.append(StagedFile(source_dir / "processed" / name, f"data/optional/{name}"))

    for name in SPLITS_CORE:
        files.append(StagedFile(source_dir / "splits" / name, f"data/splits/{name}"))

    if include_examples and examples_dir.is_dir():
        for path in sorted(examples_dir.iterdir()):
            # skip hidden files, e.g. the ModelScope upload cache (.ms_upload_cache)
            if path.is_file() and not path.name.startswith("."):
                files.append(StagedFile(path, f"examples/{path.name}"))

    for name in CARD_FILES:
        src = card_dir / name
        if src.is_file():
            files.append(StagedFile(src, name))

    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assemble the WCA-Bench release staging directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--tier",
        choices=["core", "full"],
        default="core",
        help="core = small tables + splits; full = core + scrambles/result_attempts.",
    )
    parser.add_argument(
        "--source-dir",
        default=str(DEFAULT_SOURCE),
        help="Repository data directory holding processed/ and splits/.",
    )
    parser.add_argument(
        "--examples-dir",
        default=str(DEFAULT_EXAMPLES),
        help="Directory holding baseline reports and leaderboard.",
    )
    parser.add_argument(
        "--card-dir",
        default=str(DEFAULT_CARD_DIR),
        help="Directory holding the dataset card (.gitattributes / dataset_infos.json).",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT),
        help="Staging root; the dataset is written to <out-dir>/dataset.",
    )
    parser.add_argument(
        "--no-examples",
        dest="include_examples",
        action="store_false",
        help="Skip the examples/ directory.",
    )
    parser.set_defaults(include_examples=True)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove an existing <out-dir>/dataset before staging.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the staging plan without copying anything.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    source_dir = Path(args.source_dir).expanduser().resolve()
    examples_dir = Path(args.examples_dir).expanduser().resolve()
    card_dir = Path(args.card_dir).expanduser().resolve()
    out_root = Path(args.out_dir).expanduser().resolve()
    dataset_dir = out_root / "dataset"

    files = plan_stage(args.tier, source_dir, examples_dir, card_dir, args.include_examples)

    missing = [item for item in files if not item.exists]
    total = sum(item.size for item in files)

    print("WCA-Bench release staging")
    print(f"  tier        : {args.tier}")
    print(f"  source dir  : {source_dir}")
    print(f"  examples    : {examples_dir if args.include_examples else '(skipped)'}")
    print(f"  card dir    : {card_dir}")
    print(f"  staging dir : {dataset_dir}")
    print(f"  files       : {len(files)} ({human_size(total)})")
    print("  planned copies:")
    for item in files:
        flag = "" if item.exists else "  [MISSING]"
        print(f"    - {item.rel_dst} <- {item.src.name} ({human_size(item.size)}){flag}")

    if missing:
        print(f"\n[warn] {len(missing)} source file(s) are missing and will be skipped:")
        for item in missing:
            print(f"        {item.src}")
        if any(not item.exists and item.rel_dst.startswith("data/processed") for item in missing):
            print("[error] core processed tables are missing; build the dataset first.", file=sys.stderr)
            return 2

    if args.dry_run:
        print("\n[dry-run] nothing was written.")
        return 0

    if args.clean and dataset_dir.exists():
        print(f"[1/2] cleaning {dataset_dir} ...")
        shutil.rmtree(dataset_dir)

    staged_records: list[dict] = []
    dataset_dir.mkdir(parents=True, exist_ok=True)
    print(f"[1/2] copying {len(files)} file(s) into {dataset_dir} ...")
    for item in files:
        if not item.exists:
            continue
        dst = dataset_dir / item.rel_dst
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item.src, dst)
        staged_records.append(
            {
                "path": item.rel_dst,
                "bytes": dst.stat().st_size,
                "sha256": item.sha256(),
            }
        )

    manifest = {
        "tier": args.tier,
        "source_dir": str(source_dir),
        "files": staged_records,
        "n_files": len(staged_records),
        "total_bytes": sum(record["bytes"] for record in staged_records),
        "total_human": human_size(sum(record["bytes"] for record in staged_records)),
        "layout": "publish/DATASET_LAYOUT.md",
    }
    manifest_path = dataset_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[2/2] wrote {manifest_path.name}")
    print(
        f"\n[done] staged {len(staged_records)} file(s), "
        f"{manifest['total_human']} at {dataset_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
