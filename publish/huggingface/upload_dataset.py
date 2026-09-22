#!/usr/bin/env python3
"""Create/update the WCA-Bench dataset repository on the Hugging Face Hub.

The script uploads an already staged directory (see
``publish/tools/stage_release.py``) and never touches a token written on disk: the
token is always read from an environment variable (``HF_TOKEN`` by default).

Examples
--------
Inspect what would be uploaded, with no network calls::

    python publish/huggingface/upload_dataset.py --dry-run

Real upload (public dataset)::

    set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx   # Windows (cmd.exe)
    python publish/huggingface/upload_dataset.py --repo-id Maicarons/WCA-Bench --public

Real upload (private dataset)::

    export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx  # bash
    python publish/huggingface/upload_dataset.py --repo-id Maicarons/WCA-Bench --private
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PUBLISH_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_DIR = PUBLISH_DIR / "_staging" / "dataset"
DEFAULT_REPO_ID = "Maicarons/WCA-Bench"
DEFAULT_TOKEN_ENV = "HF_TOKEN"
INSTALL_HINT = (
    "huggingface_hub is not installed. Install the publishing dependencies first:\n"
    "    python -m pip install -r publish/huggingface/requirements.txt"
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
LFS_WARN_THRESHOLD = 10 * 1024 * 1024  # 10 MiB


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
        description="Create/update the WCA-Bench dataset repository on the Hugging Face Hub.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Target Hub repository id.")
    parser.add_argument(
        "--local-dir",
        default=str(DEFAULT_LOCAL_DIR),
        help="Staged directory to upload (produced by stage_release.py).",
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help="Name of the environment variable holding the Hub token.",
    )
    parser.add_argument(
        "--revision",
        default="main",
        help="Branch/revision to commit to.",
    )
    parser.add_argument(
        "--commit-message",
        default="Upload WCA-Bench dataset",
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
        "--no-create",
        dest="create",
        action="store_false",
        help="Do not create the repository; assume it already exists.",
    )
    parser.set_defaults(create=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the upload plan and exit without any network call.",
    )
    return parser


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
    large = [path for path in files if path.stat().st_size >= LFS_WARN_THRESHOLD]

    print("WCA-Bench -> Hugging Face Hub")
    print(f"  repo id     : {args.repo_id}")
    print("  repo type   : dataset")
    print(f"  visibility  : {'private' if args.private else 'public'}")
    print(f"  revision    : {args.revision}")
    print(f"  local dir   : {local_dir}")
    print(f"  files       : {len(files)} ({human_size(total)})")
    print(f"  LFS files   : {len(large)} (>= {human_size(LFS_WARN_THRESHOLD)})")
    print("  planned files:")
    for path in files:
        rel = path.relative_to(local_dir).as_posix()
        print(f"    - {rel} ({human_size(path.stat().st_size)})")
    if large:
        print("  note: the files listed above are tracked via Git LFS (.gitattributes).")

    if args.dry_run:
        print("\n[dry-run] no network request was made.")
        return 0

    try:
        from huggingface_hub import HfApi
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

    api = HfApi(token=token)

    if args.create:
        print(f"\n[1/2] creating repository {args.repo_id} (exist_ok=True) ...")
        api.create_repo(
            repo_id=args.repo_id,
            repo_type="dataset",
            private=args.private,
            exist_ok=True,
        )

    print(f"[2/2] uploading {len(files)} file(s) from {local_dir} ...")
    api.upload_folder(
        repo_id=args.repo_id,
        repo_type="dataset",
        folder_path=str(local_dir),
        revision=args.revision,
        commit_message=args.commit_message,
        ignore_patterns=[".DS_Store"],
    )

    print(f"\n[done] dataset available at https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
