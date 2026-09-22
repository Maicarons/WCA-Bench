#!/usr/bin/env python3
"""Upload the WCA-Bench release to ModelScope (魔搭) using the ``modelscope`` SDK.

The token is always read from an environment variable (``MODELSCOPE_API_TOKEN`` by
default); it is never written to disk. The script works on a staged directory
produced by ``publish/tools/stage_release.py``.

Examples
--------
Dry-run (no network calls)::

    python publish/modelscope/upload.py --dry-run

Real upload of a dataset repository::

    set MODELSCOPE_API_TOKEN=ms-xxxxxxxxxxxxxxxx      # Windows (cmd.exe)
    python publish/modelscope/upload.py --repo-id Maicarons/WCA-Bench --repo-type dataset

Real upload of the baseline reports as a model repository::

    python publish/modelscope/upload.py \
        --repo-id Maicarons/WCA-Bench-baselines --repo-type model --local-dir publish/_staging/dataset/examples
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PUBLISH_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PUBLISH_DIR.parent
DEFAULT_LOCAL_DIR = PUBLISH_DIR / "_staging" / "dataset"
DEFAULT_REPO_ID = "Maicarons/WCA-Bench"
DEFAULT_TOKEN_ENV = "MODELSCOPE_API_TOKEN"
INSTALL_HINT = (
    "modelscope is not installed. Install the publishing dependencies first:\n"
    "    python -m pip install -r publish/modelscope/requirements.txt"
)


def load_dotenv(path: Path | None = None) -> None:
    """Best-effort load of a ``.env`` file into ``os.environ`` (no external deps).

    Only sets variables that are not already present, and never prints their values.
    This lets maintainers keep credentials in a git-ignored ``.env`` at the repo root.
    """
    if path is None:
        path = Path(__file__).resolve().parents[2] / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def human_size(num_bytes: int) -> str:
    """Return a short human-readable size string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


def collect_files(local_dir: Path) -> list[Path]:
    """Return every regular file under ``local_dir``, sorted for stable output."""
    return sorted(path for path in local_dir.rglob("*") if path.is_file())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upload the WCA-Bench release to ModelScope (魔搭).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Target ModelScope repo id.")
    parser.add_argument(
        "--repo-type",
        choices=["dataset", "model"],
        default="dataset",
        help="ModelScope repository type.",
    )
    parser.add_argument(
        "--local-dir",
        default=str(DEFAULT_LOCAL_DIR),
        help="Staged directory to upload (produced by stage_release.py).",
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help="Name of the environment variable holding the ModelScope SDK token.",
    )
    parser.add_argument(
        "--revision",
        default="master",
        help="ModelScope branch/revision to commit to.",
    )
    parser.add_argument(
        "--commit-message",
        default="Upload WCA-Bench release",
        help="Commit message used for the upload.",
    )
    privacy = parser.add_mutually_exclusive_group()
    privacy.add_argument(
        "--public",
        dest="private",
        action="store_false",
        help="Create the repository as public (default).",
    )
    privacy.add_argument(
        "--private",
        dest="private",
        action="store_true",
        help="Create the repository as private.",
    )
    parser.set_defaults(private=False)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the upload plan and exit without any network call.",
    )
    return parser


def _upload_with_hub_api(api, args, local_dir: Path) -> None:
    """Upload ``local_dir`` via ``HubApi.upload_folder`` (signature-tolerant)."""
    kwargs: dict = {
        "repo_id": args.repo_id,
        "folder_path": str(local_dir),
        "commit_message": args.commit_message,
        "revision": args.revision,
    }
    try:
        api.upload_folder(**kwargs, repo_type=args.repo_type)
    except TypeError:
        # Older SDKs only support the model repository layout.
        api.upload_folder(**kwargs)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    local_dir = Path(args.local_dir).expanduser().resolve()
    if not local_dir.is_dir():
        print(f"[error] local directory does not exist: {local_dir}", file=sys.stderr)
        print(
            "        Run `python publish/tools/stage_release.py --tier core` first.",
            file=sys.stderr,
        )
        return 2

    files = collect_files(local_dir)
    if not files:
        print(f"[error] no files found under: {local_dir}", file=sys.stderr)
        return 2

    total = sum(path.stat().st_size for path in files)

    print("WCA-Bench -> ModelScope")
    print(f"  repo id     : {args.repo_id}")
    print(f"  repo type   : {args.repo_type}")
    print(f"  visibility  : {'private' if args.private else 'public'}")
    print(f"  revision    : {args.revision}")
    print(f"  local dir   : {local_dir}")
    print(f"  files       : {len(files)} ({human_size(total)})")
    print("  planned files:")
    for path in files:
        rel = path.relative_to(local_dir).as_posix()
        print(f"    - {rel} ({human_size(path.stat().st_size)})")

    if args.dry_run:
        print("\n[dry-run] no network request was made.")
        return 0

    try:
        from modelscope.hub.api import HubApi
    except ImportError:
        print(f"\n[error] {INSTALL_HINT}", file=sys.stderr)
        return 1

    load_dotenv()  # fill from repo-root .env when the env var is not already set
    token = os.environ.get(args.token_env)
    if not token:
        print(
            f"\n[error] environment variable {args.token_env!r} is not set; refusing to "
            "upload without credentials.",
            file=sys.stderr,
        )
        return 1

    api = HubApi()
    login = getattr(api, "login", None)
    if callable(login):
        login(token)

    print(
        f"\n[1/2] creating repository {args.repo_id} "
        f"(repo_type={args.repo_type}, private={args.private}, exist_ok=True) ..."
    )
    try:
        api.create_repo(
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            private=args.private,
        )
    except Exception as exc:  # noqa: BLE001 - repository may already exist
        print(f"        [warn] create_repo skipped: {exc}", file=sys.stderr)

    print(f"[2/2] uploading {len(files)} file(s) from {local_dir} ...")
    try:
        _upload_with_hub_api(api, args, local_dir)
    except Exception as exc:  # noqa: BLE001 - surface SDK errors clearly
        print(f"\n[error] ModelScope upload failed: {exc}", file=sys.stderr)
        print(
            "        Alternative: MsDataset.upload(...) with the same repo id, or check that "
            "the repository exists and the token has write access.",
            file=sys.stderr,
        )
        return 1

    print(f"\n[done] release available at https://www.modelscope.cn/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
