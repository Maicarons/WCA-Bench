"""Compute-device resolution shared by the torch / XGBoost baselines.

WCA-Bench defaults to **CPU** to keep results reproducible. ``auto`` opts into
CUDA when it is actually available; an explicit ``cpu``/``cuda`` value (or the
``WCA_BENCH_DEVICE`` environment variable) always wins.
"""

from __future__ import annotations

import os

DEFAULT_DEVICE = "cpu"


def resolve_device(device: str | None = DEFAULT_DEVICE) -> str:
    """Resolve a requested device to ``"cpu"`` or a ``"cuda"`` string.

    - ``None`` falls back to ``WCA_BENCH_DEVICE`` then ``"cpu"``.
    - ``"auto"`` selects CUDA when available, else CPU.
    - ``"cuda"``/``"cuda:<idx>"`` degrades to CPU when torch/CUDA is missing.
    """
    if device is None:
        device = os.environ.get("WCA_BENCH_DEVICE", DEFAULT_DEVICE)
    device = str(device).lower()
    if device == "auto":
        return "cuda" if _cuda_available() else "cpu"
    if device.startswith("cuda") and not _cuda_available():
        return "cpu"
    return device


def _cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def device_label(device: str) -> str:
    """Human-readable device label, e.g. ``cuda:NVIDIA A100`` / ``cpu``."""
    device = resolve_device(device)
    if not str(device).startswith("cuda"):
        return "cpu"
    try:
        import torch

        if torch.cuda.is_available():
            return f"cuda:{torch.cuda.get_device_name(0)}"
    except Exception:
        pass
    return "cpu"
