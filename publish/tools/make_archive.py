#!/usr/bin/env python3
"""Create distributable archives (and SHA256 manifests) of a staged release.

Reads a staged directory (``publish/_staging`` by default, as produced by
``publish/tools/stage_release.py``) and writes:

* ``wca-bench-<name>.tar.gz`` — gzip-compressed tarball of the staged tree.
* ``wca-bench-<name>.zip``    — ZIP archive (optional, ``--format``).
* ``MANIFEST.sha256``         — per-file SHA256 of the staged tree.
* ``SHA256SUMS``              — SHA256 of each produced archive.

Outputs go to ``publish/dist`` by default. Archives are large; they are not meant
to be committed to Git (see ``publish/README.md``).

Examples
--------
Dry-run::

    python publish/tools/make_archive.py --dry-run

Create both archives::

    python publish/tools/make_archive.py --format both --name core
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tarfile
import zipfile
from pathlib import Path

PUBLISH_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PUBLISH_DIR / "_staging"
DEFAULT_OUT = PUBLISH_DIR / "dist"

# Files that should not end up inside a distributable archive.
EXCLUDE_NAMES = {"RELEASE_MANIFEST.json"}


def human_size(num_bytes: int) -> str:
    """Return a short human-readable size string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


def sha256_of(path: Path, chunk_size: int = 1 << 20) -> str:
    """Return the SHA256 hex digest of ``path``."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_payload(root: Path) -> list[Path]:
    """Return the files to archive, relative to ``root`` and sorted."""
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.name not in EXCLUDE_NAMES
    ]
    return sorted(files)


def find_payload_roots(input_dir: Path) -> list[Path]:
    """Return the dataset directories to archive.

    Accepts either a staging root containing a ``dataset/`` sub-directory or the
    dataset directory itself.
    """
    dataset = input_dir / "dataset"
    if dataset.is_dir():
        return [dataset]
    return [input_dir]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive a staged WCA-Bench release and emit SHA256 manifests.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT),
        help="Staging root (expects <input>/dataset) or the dataset dir itself.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT),
        help="Directory receiving the archives and checksum files.",
    )
    parser.add_argument(
        "--name",
        default="release",
        help="Archive base name, e.g. core -> wca-bench-core.tar.gz.",
    )
    parser.add_argument(
        "--format",
        choices=["tar.gz", "zip", "both"],
        default="both",
        help="Archive format(s) to produce.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the archive plan without writing anything.",
    )
    return parser


def write_tar_gz(dataset_dir: Path, payload: list[Path], out_path: Path) -> None:
    """Write a gzip-compressed tarball containing ``payload``."""
    with tarfile.open(out_path, "w:gz") as tar:
        for path in payload:
            arcname = Path("wca-bench") / path.relative_to(dataset_dir)
            tar.add(path, arcname=arcname.as_posix())


def write_zip(dataset_dir: Path, payload: list[Path], out_path: Path) -> None:
    """Write a ZIP archive containing ``payload``."""
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in payload:
            arcname = (Path("wca-bench") / path.relative_to(dataset_dir)).as_posix()
            archive.write(path, arcname=arcname)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not input_dir.is_dir():
        print(f"[error] input directory does not exist: {input_dir}", file=sys.stderr)
        print(
            "        Run `python publish/tools/stage_release.py --tier core` first.",
            file=sys.stderr,
        )
        return 2

    payload_roots = find_payload_roots(input_dir)
    dataset_dir = payload_roots[0]
    payload = collect_payload(dataset_dir)
    if not payload:
        print(f"[error] no payload files found under: {dataset_dir}", file=sys.stderr)
        return 2

    total = sum(path.stat().st_size for path in payload)
    tar_path = out_dir / f"wca-bench-{args.name}.tar.gz"
    zip_path = out_dir / f"wca-bench-{args.name}.zip"
    manifest_path = out_dir / "MANIFEST.sha256"
    sums_path = out_dir / "SHA256SUMS"

    formats = ["tar.gz", "zip"] if args.format == "both" else [args.format]

    print("WCA-Bench release archiving")
    print(f"  input dir   : {dataset_dir}")
    print(f"  out dir     : {out_dir}")
    print(f"  payload     : {len(payload)} file(s) ({human_size(total)})")
    print(f"  formats     : {', '.join(formats)}")
    print("  planned outputs:")
    for fmt in formats:
        print(f"    - {(tar_path if fmt == 'tar.gz' else zip_path).name}")
    print(f"    - {manifest_path.name} (per-file SHA256)")
    print(f"    - {sums_path.name} (archive SHA256)")

    if args.dry_run:
        print("\n[dry-run] nothing was written.")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] writing per-file manifest ({len(payload)} entries) ...")
    manifest_lines = [
        f"{sha256_of(path)}  {path.relative_to(dataset_dir).as_posix()}" for path in payload
    ]
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print("[2/3] writing archive(s) ...")
    produced: list[Path] = []
    if "tar.gz" in formats:
        write_tar_gz(dataset_dir, payload, tar_path)
        produced.append(tar_path)
    if "zip" in formats:
        write_zip(dataset_dir, payload, zip_path)
        produced.append(zip_path)

    print("[3/3] writing archive checksums ...")
    sums_lines = [f"{sha256_of(path)}  {path.name}" for path in produced]
    sums_path.write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

    print("\n[done] produced:")
    for path in produced:
        print(f"    - {path} ({human_size(path.stat().st_size)})")
    print(f"    - {manifest_path}")
    print(f"    - {sums_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
