#!/usr/bin/env python
"""Download WCA Results Export (v2 TSV) into data/raw."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://www.worldcubeassociation.org/api/v0/export/public"
DEFAULT_RAW = ROOT / "data" / "raw"


def fetch_export_meta() -> dict:
    with urllib.request.urlopen(API_URL, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {dest}")
    # prefer curl for resume/retry robustness on large exports
    curl = shutil.which("curl") or shutil.which("curl.exe")
    if curl:
        cmd = [curl, "-L", "--retry", "5", "--retry-delay", "3", "-C", "-", "-o", str(dest), url]
        subprocess.check_call(cmd)
        if dest.exists() and dest.stat().st_size > 0:
            return dest
    # fallback: streaming urllib with retries
    last_err = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp, open(dest, "wb") as f:
                shutil.copyfileobj(resp, f)
            return dest
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(2 + attempt)
    raise RuntimeError(f"download failed: {last_err}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download WCA official public export")
    parser.add_argument("--out", type=Path, default=DEFAULT_RAW)
    parser.add_argument(
        "--format",
        choices=["tsv", "sql"],
        default="tsv",
        help="Export format; tsv is recommended for WCA-Bench",
    )
    args = parser.parse_args(argv)

    meta = fetch_export_meta()
    print(json.dumps(meta, indent=2)[:800])
    url = meta.get("tsv_url") if args.format == "tsv" else meta.get("sql_url")
    if not url:
        print("API did not return export URL", file=sys.stderr)
        return 1
    zip_path = args.out / Path(url).name
    if zip_path.suffix != ".zip":
        zip_path = args.out / f"WCA_export_{args.format}.zip"
    download(url, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(args.out)
    meta_path = args.out / "export_api_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    report = {
        "export_date": meta.get("export_date"),
        "export_version": meta.get("export_version"),
        "format": args.format,
        "zip": str(zip_path),
        "out_dir": str(args.out),
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "data_ingest.md").write_text(
        "# WCA Export Ingest\n\n```json\n" + json.dumps(report, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    print("Done:", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
