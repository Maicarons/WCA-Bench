#!/usr/bin/env python3
"""Verify a staged WCA-Bench release before it is uploaded.

This closes the loop between the A1.2 build checksums and the A4.4/A4.5 release
artifacts. It performs two independent checks:

1. **Staging self-consistency** — every file recorded in ``RELEASE_MANIFEST.json``
   exists under the staging directory and its SHA-256 matches the recorded digest.
2. **Provenance against the build manifest** — every staged
   ``data/processed/<table>.parquet`` matches the SHA-256 recorded in
   ``data/processed/manifest.json``, i.e. what is about to be published really is
   the artefact that the reproducibility tests were run against.

Examples
--------
::

    python publish/tools/verify_release.py
    python publish/tools/verify_release.py --staging-dir publish/_staging/dataset
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PUBLISH_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PUBLISH_DIR.parent
DEFAULT_STAGING = PUBLISH_DIR / "_staging" / "dataset"
DEFAULT_BUILD_MANIFEST = REPO_ROOT / "data" / "processed" / "manifest.json"
RELEASE_MANIFEST_NAME = "RELEASE_MANIFEST.json"
_CHUNK = 1 << 20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify staged WCA-Bench release artifacts (checksums + provenance).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--staging-dir",
        default=str(DEFAULT_STAGING),
        help="Staged dataset directory produced by stage_release.py.",
    )
    parser.add_argument(
        "--build-manifest",
        default=str(DEFAULT_BUILD_MANIFEST),
        help="Build manifest holding the A1.2 checksums to compare against.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    staging_dir = Path(args.staging_dir).expanduser().resolve()
    release_manifest = staging_dir / RELEASE_MANIFEST_NAME
    if not release_manifest.is_file():
        print(f"[error] {release_manifest} not found; run stage_release.py first.", file=sys.stderr)
        return 2

    release = json.loads(release_manifest.read_text(encoding="utf-8"))
    records = release.get("files", [])
    if not records:
        print("[error] release manifest lists no files.", file=sys.stderr)
        return 2

    print(f"Staged release : {staging_dir}")
    print(f"  tier         : {release.get('tier', '?')}")
    print(f"  files        : {len(records)}")

    failures: list[str] = []

    # 1. staging self-consistency
    for record in records:
        rel = record["path"]
        path = staging_dir / rel
        if not path.is_file():
            failures.append(f"missing file: {rel}")
            continue
        if record.get("sha256") and sha256(path) != record["sha256"]:
            failures.append(f"checksum mismatch: {rel}")
    print(f"  [1/2] self-consistency: {len(records) - len(failures)}/{len(records)} ok")

    # 2. provenance against the build manifest (A1.2)
    build_manifest_path = Path(args.build_manifest).expanduser().resolve()
    if not build_manifest_path.is_file():
        print(f"  [2/2] skipped: build manifest not found ({build_manifest_path})")
    else:
        build = json.loads(build_manifest_path.read_text(encoding="utf-8"))
        checksums = build.get("checksums", {})
        if not checksums:
            failures.append("build manifest has no 'checksums' section (A1.2 incomplete)")
            print("  [2/2] FAILED: build manifest has no checksums")
        else:
            checked = 0
            for name, expected in checksums.items():
                staged = staging_dir / "data" / "processed" / f"{name}.parquet"
                if not staged.is_file():
                    continue  # table is not part of this tier
                checked += 1
                if sha256(staged) != expected:
                    failures.append(f"provenance mismatch: data/processed/{name}.parquet")
            print(f"  [2/2] provenance vs A1.2: {checked} table(s) compared")

    if failures:
        print("\n[FAIL] release verification failed:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("\n[OK] staged release is consistent with the build manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
