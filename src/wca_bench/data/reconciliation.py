"""Reproducibility helpers: file checksums and average-of-X agreement.

These functions support acceptance criteria A1.2 (repeated runs produce
identical SHA-256 checksums) and A1.4 (reconstructed averages agree with the
official stored ``average`` field at >= 99.5%).

The data package does NOT import from ``tasks``, ``baselines``,
``evaluation`` or ``leaderboard`` (enforced by ``tests/unit/test_import_policy``),
so this module only depends on ``decoders`` and ``schema``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from wca_bench.data.decoders import compute_average, decode_result_value
from wca_bench.data.schema import FORMATS

_CHUNK = 1 << 20  # 1 MiB


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_checksums(tables: dict[str, Any]) -> dict[str, str]:
    """Return ``{table_name: sha256_hex}`` for every existing file in ``tables``."""
    checksums: dict[str, str] = {}
    for name, path in tables.items():
        p = Path(path)
        if p.exists() and p.is_file():
            checksums[name] = _sha256(p)
    return checksums


def verify_checksums(processed_dir: str | Path, manifest: dict[str, Any]) -> bool:
    """Raise if any recorded checksum does not match the file on disk.

    Resolves the file by the stored absolute path first, then falls back to
    ``processed_dir / f"{name}.parquet"`` and ``processed_dir / f"{name}.csv"``
    so the check survives a moved working directory.
    """
    processed_dir = Path(processed_dir)
    tables = manifest.get("tables", {})
    checksums = manifest.get("checksums", {})
    if not checksums:
        raise ValueError("manifest has no 'checksums' section")
    for name, expected in checksums.items():
        candidates = [Path(tables[name])] if name in tables else []
        candidates += [
            processed_dir / f"{name}.parquet",
            processed_dir / f"{name}.csv",
        ]
        found = next((c for c in candidates if c.exists() and c.is_file()), None)
        if found is None:
            raise FileNotFoundError(f"cannot locate file for table '{name}'")
        actual = _sha256(found)
        if actual != expected:
            raise AssertionError(
                f"checksum mismatch for '{name}': {actual} != {expected}"
            )
    return True


def compute_average_agreement(
    results: pd.DataFrame,
    result_attempts: pd.DataFrame,
) -> dict[str, float]:
    """Reconstruct ``average`` from attempt values and compare to the stored field.

    Only rows whose round format actually produces an average (average-of-5 /
    mean-of-3) and whose stored ``average`` is a positive integer are compared.

    Returns ``{"agreement": rate, "n_compared": n, "n_match": m}``.
    """
    required = {"result_id", "attempt_number", "value"}
    if result_attempts is None or result_attempts.empty or not required.issubset(result_attempts.columns):
        return {"agreement": 1.0, "n_compared": 0, "n_match": 0}

    attempts_by_result: dict[Any, list[int]] = (
        result_attempts.sort_values(["result_id", "attempt_number"])
        .groupby("result_id")["value"]
        .apply(list)
        .to_dict()
    )

    n_compared = 0
    n_match = 0
    for row in results.itertuples(index=False):
        fmt_id = getattr(row, "format_id", None)
        if fmt_id is None:
            continue
        fmt = FORMATS.get(str(fmt_id))
        if fmt is None or not fmt.get("average"):
            continue
        stored = int(getattr(row, "average", 0) or 0)
        if stored <= 0:  # DNF (-1) or no average (0)
            continue
        vals = attempts_by_result.get(getattr(row, "id", None))
        if not vals:
            continue
        event_id = getattr(row, "event_id", "333")
        decoded = [decode_result_value(v, event_id) for v in vals]
        reconstructed = int(compute_average(decoded, fmt["id"], event_id))
        n_compared += 1
        if reconstructed == stored:
            n_match += 1

    agreement = (n_match / n_compared) if n_compared else 1.0
    return {"agreement": agreement, "n_compared": n_compared, "n_match": n_match}
