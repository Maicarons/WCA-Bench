#!/usr/bin/env python3
"""Generate result figures for the WCA-Bench paper.

The figures are produced directly from the *real* leaderboard artifact that
ships with the repository, so that every value plotted in the paper can be
traced back to a measured baseline result.

Data source
-----------
``<repo-root>/examples/leaderboard.csv`` -- one row per (task, model) with the
primary metric, its value and the number of evaluated instances.

Output
------
``fig1_task_overview.pdf``        four-panel comparison across T1/T2/T3/T5
``fig2_result_prediction.pdf``    T1 MAE(log) by baseline model
``fig3_dnf_models.pdf``           T3 AUC-PR / AUC-ROC by baseline model
``fig4_transfer_pairs.pdf``       T5 number of identifiable event pairs

The script is offline and deterministic. It exits with a clear message and a
non-zero status if the CSV is missing or lacks the expected columns.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless / batch rendering

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
HERE = Path(__file__).resolve().parent          # paper/figures
REPO_ROOT = HERE.parent.parent                  # repository root
CSV_PATH = REPO_ROOT / "examples" / "leaderboard.csv"
OUT_DIR = HERE

REQUIRED_COLUMNS = {"task", "model", "primary_metric", "primary_value"}

# A small, consistent palette.
C_METHOD = "#1F4E79"   # methodological baselines
C_DOMAIN = "#1E6B52"   # domain baselines
C_TRIVIAL = "#B03A2E"  # trivial / correlational baselines

FAMILY_COLORS = {
    "method": C_METHOD,
    "domain": C_DOMAIN,
    "trivial": C_TRIVIAL,
    "statistical": "#7D3C98",
}

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": ":",
    }
)


def load_leaderboard() -> pd.DataFrame:
    """Read and validate the leaderboard CSV.

    Raises a ``SystemExit`` with a helpful message when the file is absent or
    malformed, so the Makefile target fails loudly instead of producing empty
    figures.
    """
    if not CSV_PATH.exists():
        sys.stderr.write(
            "ERROR: leaderboard CSV not found.\n"
            f"  expected at: {CSV_PATH}\n"
            "  Generate it with:  python scripts/build_leaderboard.py\n"
        )
        raise SystemExit(1)

    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"ERROR: could not parse {CSV_PATH}: {exc}\n")
        raise SystemExit(1)

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        sys.stderr.write(
            f"ERROR: {CSV_PATH} is missing required columns: {sorted(missing)}\n"
        )
        raise SystemExit(1)

    df = df.copy()
    df["primary_value"] = pd.to_numeric(df["primary_value"], errors="coerce")
    return df


def _values(df: pd.DataFrame, task: str) -> pd.DataFrame:
    """Return the rows for one task, sorted by model name, with valid values."""
    sub = df[df["task"] == task].copy()
    sub = sub.dropna(subset=["primary_value"])
    return sub.sort_values("primary_value", ascending=False)


def _classify(model: str) -> str:
    """Heuristic family label used only for colouring the bars."""
    name = model.lower()
    if any(k in name for k in ("xgboost", "forest", "plackett", "did", "causal")):
        return "method"
    if any(k in name for k in ("psych", "historical", "kde")):
        return "domain"
    if any(k in name for k in ("history", "spearman", "correlation")):
        return "trivial"
    return "statistical"


def _barh(ax, labels, values, title, xlabel, colorize=True) -> None:
    colors = [FAMILY_COLORS[_classify(m)] for m in labels] if colorize else C_METHOD
    bars = ax.barh(range(len(values)), values, color=colors, height=0.6)
    ax.set_yticks(range(len(values)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    span = max(values) if len(values) else 1.0
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_width() + 0.01 * span,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}",
            va="center",
            fontsize=8,
        )
    ax.set_xlim(0, span * 1.18)


def figure_task_overview(df: pd.DataFrame) -> Path:
    """Four-panel overview: the best baseline of each principal metric task."""
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.2))

    # T1: result prediction, MAE(log) -- lower is better.
    t1 = _values(df, "result_prediction")
    _barh(
        axes[0, 0],
        list(t1["model"]),
        list(t1["primary_value"]),
        r"T1 result prediction ($\mathrm{MAE}_{\log}$, lower better)",
        r"$\mathrm{MAE}_{\log}$",
    )

    # T2: placement, Kendall tau -- higher is better.
    t2 = _values(df, "placement")
    axes[0, 1].barh(
        range(len(t2)),
        t2["primary_value"],
        color=[FAMILY_COLORS[_classify(m)] for m in t2["model"]],
        height=0.6,
    )
    axes[0, 1].set_yticks(range(len(t2)))
    axes[0, 1].set_yticklabels(list(t2["model"]))
    axes[0, 1].invert_yaxis()
    axes[0, 1].set_title(r"T2 placement (Kendall $\tau$, higher better)")
    axes[0, 1].set_xlabel(r"Kendall $\tau$")
    axes[0, 1].set_xlim(0, 1.0)
    for i, v in enumerate(t2["primary_value"]):
        axes[0, 1].text(v + 0.02, i, f"{v:.4f}", va="center", fontsize=8)

    # T3: DNF prediction, AUC-PR -- higher is better.
    t3 = _values(df, "dnf")
    axes[1, 0].barh(
        range(len(t3)),
        t3["primary_value"],
        color=[FAMILY_COLORS[_classify(m)] for m in t3["model"]],
        height=0.6,
    )
    axes[1, 0].set_yticks(range(len(t3)))
    axes[1, 0].set_yticklabels(list(t3["model"]))
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_title("T3 DNF prediction (AUC-PR, higher better)")
    axes[1, 0].set_xlabel("AUC-PR")
    axes[1, 0].set_xlim(0, max(t3["primary_value"]) * 1.25 if len(t3) else 1.0)
    for i, v in enumerate(t3["primary_value"]):
        axes[1, 0].text(v + 0.01, i, f"{v:.4f}", va="center", fontsize=8)

    # T5: transfer, number of identifiable pairs -- higher is better.
    t5 = _values(df, "transfer")
    axes[1, 1].barh(
        range(len(t5)),
        t5["primary_value"],
        color=[FAMILY_COLORS[_classify(m)] for m in t5["model"]],
        height=0.6,
    )
    axes[1, 1].set_yticks(range(len(t5)))
    axes[1, 1].set_yticklabels(list(t5["model"]))
    axes[1, 1].invert_yaxis()
    axes[1, 1].set_title("T5 skill transfer (identifiable pairs)")
    axes[1, 1].set_xlabel("# identifiable event pairs")
    axes[1, 1].set_xlim(0, max(t5["primary_value"]) * 1.25 if len(t5) else 1.0)
    for i, v in enumerate(t5["primary_value"]):
        axes[1, 1].text(v + 3, i, f"{int(round(v))}", va="center", fontsize=8)

    fig.suptitle("WCA-Bench reference baselines (sampled test set)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = OUT_DIR / "fig1_task_overview.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


def figure_result_prediction(df: pd.DataFrame) -> Path:
    """T1: baseline models ranked by MAE(log)."""
    sub = _values(df, "result_prediction")
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    _barh(
        ax,
        list(sub["model"]),
        list(sub["primary_value"]),
        r"T1 result prediction: $\mathrm{MAE}_{\log}$ by baseline",
        r"$\mathrm{MAE}_{\log}$ (lower is better)",
    )
    fig.tight_layout()
    out = OUT_DIR / "fig2_result_prediction.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


def figure_dnf_models(df: pd.DataFrame) -> Path:
    """T3: AUC-PR for the registered DNF baselines."""
    sub = _values(df, "dnf")
    fig, ax = plt.subplots(figsize=(5.4, 2.4))
    _barh(
        ax,
        list(sub["model"]),
        list(sub["primary_value"]),
        "T3 DNF prediction: AUC-PR by baseline",
        "AUC-PR (higher is better)",
    )
    fig.tight_layout()
    out = OUT_DIR / "fig3_dnf_models.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


def figure_transfer_pairs(df: pd.DataFrame) -> Path:
    """T5: number of identifiable event pairs per estimator."""
    sub = _values(df, "transfer")
    fig, ax = plt.subplots(figsize=(5.4, 2.4))
    _barh(
        ax,
        list(sub["model"]),
        list(sub["primary_value"]),
        "T5 skill transfer: identifiable event pairs",
        "# identifiable event pairs (higher is better)",
    )
    fig.tight_layout()
    out = OUT_DIR / "fig4_transfer_pairs.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


def main() -> int:
    df = load_leaderboard()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    produced = [
        figure_task_overview(df),
        figure_result_prediction(df),
        figure_dnf_models(df),
        figure_transfer_pairs(df),
    ]

    print(f"Source: {CSV_PATH}")
    n_valid = int(df["primary_value"].notna().sum())
    print(f"Rows: {len(df)} ({n_valid} with a usable primary value)")
    for path in produced:
        print(f"Wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
