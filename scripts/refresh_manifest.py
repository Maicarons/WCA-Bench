#!/usr/bin/env python3
"""Refresh the A1.2 / A1.4 reproducibility fields of an existing manifest.

``wca_bench.data.loader.build_dataset`` writes ``checksums`` (A1.2) and
``average_agreement`` (A1.4) into ``data/processed/manifest.json``. Manifests that
were produced before those fields existed can be refreshed **in place** from the
already-built tables, which avoids a full rebuild from the raw WCA export.

Examples
--------
Preview the refresh without writing::

    python scripts/refresh_manifest.py --dry-run

Refresh the default manifest::

    python scripts/refresh_manifest.py

Skip the (heavier) average-agreement recomputation::

    python scripts/refresh_manifest.py --no-agreement
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED = REPO_ROOT / "data" / "processed"
DEFAULT_MANIFEST = DEFAULT_PROCESSED / "manifest.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh checksums and average-agreement fields in a build manifest.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--processed-dir",
        default=str(DEFAULT_PROCESSED),
        help="Directory holding the built tables referenced by the manifest.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="Manifest file to refresh (rewritten in place).",
    )
    parser.add_argument(
        "--no-agreement",
        dest="agreement",
        action="store_false",
        help="Skip recomputing the A1.4 average-agreement fields.",
    )
    parser.set_defaults(agreement=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resulting manifest without writing it.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    from wca_bench.data.reconciliation import compute_average_agreement, compute_checksums

    processed_dir = Path(args.processed_dir).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.is_file():
        print(f"[error] manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tables = manifest.get("tables", {})
    if not tables:
        print("[error] manifest has no 'tables' section; rebuild the dataset.", file=sys.stderr)
        return 2

    # A1.2: content checksums for every table that exists on disk.
    checksums = compute_checksums(tables)
    manifest["checksums"] = checksums
    print(f"  checksums   : {len(checksums)} table(s)")

    # A1.4: reconstructed-average agreement against the official stored average.
    if args.agreement:
        results_path = processed_dir / "results.parquet"
        attempts_path = processed_dir / "result_attempts.parquet"
        if not (results_path.is_file() and attempts_path.is_file()):
            print("[warn] results/result_attempts missing; skipped average agreement.")
        else:
            results = pd.read_parquet(results_path)
            attempts = pd.read_parquet(attempts_path)
            rep = compute_average_agreement(results, attempts)
            reconciliation = manifest.setdefault("reconciliation", {})
            reconciliation.update(
                {
                    "average_agreement": round(float(rep["agreement"]), 6),
                    "average_agreement_n": int(rep["n_compared"]),
                    "average_agreement_match": int(rep["n_match"]),
                }
            )
            print(
                f"  agreement   : {rep['agreement']:.6f} "
                f"({rep['n_match']}/{rep['n_compared']})"
            )

    if args.dry_run:
        print("\n[dry-run] manifest not written.")
        print(json.dumps(manifest, indent=2)[:2000])
        return 0

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n[done] refreshed {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
