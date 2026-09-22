#!/usr/bin/env python3
"""Publish the WCA-Bench community leaderboard Space to the Hugging Face Hub.

The Space is a Gradio application that renders the official leaderboard and lets
participants submit their own results. It does not run any training or
evaluation: participants evaluate locally on the frozen test split and submit
the resulting report JSON.

Examples
--------
Dry-run::

    python publish/huggingface/upload_space.py --dry-run

Publish::

    python publish/huggingface/upload_space.py --repo-id Maicarons/WCA-Bench-leaderboard
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PUBLISH_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PUBLISH_DIR.parent
DEFAULT_LOCAL_DIR = REPO_ROOT / "space"
DEFAULT_REPO_ID = "Maicarons/WCA-Bench-leaderboard"
DEFAULT_TOKEN_ENV = "HF_TOKEN"
INSTALL_HINT = (
    "huggingface_hub is not installed. Install the publishing dependencies first:\n"
    "    python -m pip install -r publish/huggingface/requirements.txt"
)

#: Directories that must never reach the Space (staging output, caches).
EXCLUDED_DIRS = {"__pycache__", ".ipynb_checkpoints", ".git"}
EXCLUDED_PREFIXES = ("_", ".")


def load_dotenv(path: Path | None = None) -> None:
    """Best-effort load of a ``.env`` file into ``os.environ`` (no external deps).

    Only sets variables that are not already present, and never prints values.
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


def collect_files(local_dir: Path) -> list[Path]:
    """Return every publishable file under ``local_dir``, sorted for stability."""
    files: list[Path] = []
    for path in sorted(local_dir.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(local_dir)
        if any(part in EXCLUDED_DIRS or part.startswith(EXCLUDED_PREFIXES)
               for part in relative.parts[:-1]):
            continue
        if relative.name.startswith(".") and relative.name != ".gitattributes":
            continue
        files.append(path)
    return files


def human_size(num_bytes: int) -> str:
    """Return a short human-readable size string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish the WCA-Bench leaderboard Space to the Hugging Face Hub.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Target Hub Space id.")
    parser.add_argument(
        "--local-dir",
        default=str(DEFAULT_LOCAL_DIR),
        help="Directory holding the Space application (defaults to ./space).",
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help="Name of the environment variable holding the Hub token.",
    )
    parser.add_argument("--revision", default="main", help="Branch/revision to commit to.")
    parser.add_argument(
        "--commit-message",
        default="Publish WCA-Bench leaderboard Space",
        help="Commit message used for the upload.",
    )
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


def upload(api, repo_id: str, revision: str, commit_message: str,
           files: list[Path], local_dir: Path) -> None:
    """Upload the Space files, falling back to per-file uploads.

    ``upload_folder`` first talks to the Hub's metadata validation endpoint,
    which is unreliable from some networks. When that step fails we fall back to
    individual ``upload_file`` calls, which skip it.
    """
    try:
        api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=str(local_dir),
            revision=revision,
            commit_message=commit_message,
            allow_patterns=None,
            ignore_patterns=["__pycache__/**", "**/__pycache__/**", "_submissions/**",
                             "**/_submissions/**", ".DS_Store"],
        )
        print(f"[done] uploaded {len(files)} file(s) via upload_folder.")
        return
    except Exception as exc:  # noqa: BLE001 - fall back to per-file uploads
        print(f"[warn] bulk upload failed ({exc.__class__.__name__}); "
              "falling back to per-file uploads.")

    uploaded = 0
    for path in files:
        try:
            api.upload_file(
                repo_id=repo_id,
                repo_type="space",
                path_or_fileobj=str(path),
                path_in_repo=path.relative_to(local_dir).as_posix(),
                revision=revision,
                commit_message=commit_message,
            )
            uploaded += 1
            print(f"  [ok] {path.relative_to(local_dir).as_posix()}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"  [FAIL] {path.relative_to(local_dir).as_posix()}: {exc}")
    print(f"[done] uploaded {uploaded}/{len(files)} file(s).")
    if uploaded < len(files):
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    local_dir = Path(args.local_dir).expanduser().resolve()
    if not local_dir.is_dir():
        print(f"[error] local directory does not exist: {local_dir}", file=sys.stderr)
        return 2

    files = collect_files(local_dir)
    if not files:
        print(f"[error] no files found under: {local_dir}", file=sys.stderr)
        return 2

    total = sum(path.stat().st_size for path in files)

    print("WCA-Bench leaderboard -> Hugging Face Hub (space)")
    print(f"  repo id     : {args.repo_id}")
    print(f"  visibility  : public")
    print(f"  revision    : {args.revision}")
    print(f"  local dir   : {local_dir}")
    print(f"  files       : {len(files)} ({human_size(total)})")
    print("  planned files:")
    for path in files:
        rel = path.relative_to(local_dir).as_posix()
        print(f"    - {rel} ({human_size(path.stat().st_size)})")

    if not (local_dir / "README.md").is_file():
        print("[error] README.md with Space metadata is required.", file=sys.stderr)
        return 2

    if args.dry_run:
        print("\n[dry-run] no network request was made.")
        return 0

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print(f"\n[error] {INSTALL_HINT}", file=sys.stderr)
        return 1

    load_dotenv()
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
        try:
            api.create_repo(
                repo_id=args.repo_id,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True,
            )
        except Exception as exc:  # noqa: BLE001 - repo may already exist
            print(f"  [warn] create_repo failed, assuming it exists: {exc}")

    print(f"[2/2] uploading {len(files)} file(s) from {local_dir} ...")
    upload(api, args.repo_id, args.revision, args.commit_message, files, local_dir)
    print(f"\n[done] space available at https://huggingface.co/spaces/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
