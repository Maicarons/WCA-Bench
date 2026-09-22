"""Configuration constants shared by the WCA-Bench leaderboard Space."""

from __future__ import annotations

import os

# --------------------------------------------------------------------------- #
# Data sources (overridable through Space secrets / environment variables)
# --------------------------------------------------------------------------- #

#: Hugging Face *dataset* repository that ships the frozen splits and the
#: official ``leaderboard.csv`` produced by the maintainers.
HF_DATASET_REPO = os.environ.get("WCA_DATASET_REPO", "Maicarons/WCA-Bench")

#: Path of the leaderboard file inside the dataset repository.
LEADERBOARD_FILENAME = os.environ.get("WCA_LEADERBOARD_FILE", "examples/leaderboard.csv")

#: ModelScope mirror of the same dataset (for users with faster CN access).
MS_DATASET_URL = os.environ.get(
    "WCA_MS_DATASET_URL", "https://www.modelscope.cn/datasets/Mai2026/WCA-Bench"
)

#: GitHub repository receiving community submissions.
GITHUB_REPO = os.environ.get("WCA_SUBMISSIONS_REPO", "Maicarons/WCA-Bench")

#: Directory (inside the repository) where community entries are stored.
COMMUNITY_DIR = "community-submissions"

# --------------------------------------------------------------------------- #
# Task definitions. Mirrors ``src/wca_bench/leaderboard/builder.PRIMARY_METRICS``.
# --------------------------------------------------------------------------- #

TASKS: dict[str, dict[str, str]] = {
    "result_prediction": {
        "primary_metric": "mae_log",
        "direction": "lower",
        "title": "Result prediction (T1)",
        "question": "Predict a competitor's result in a given round.",
        "unit": "competition-event-round (log-scale)",
    },
    "placement": {
        "primary_metric": "kendall_tau",
        "direction": "higher",
        "title": "Placement prediction (T2)",
        "question": "Rank all competitors of a round.",
        "unit": "round",
    },
    "dnf": {
        "primary_metric": "auc_pr",
        "direction": "higher",
        "title": "DNF prediction (T3)",
        "question": "Predict whether an attempt ends in a DNF.",
        "unit": "attempt",
    },
    "limit": {
        "primary_metric": "mean_loo_std",
        "direction": "lower",
        "title": "Human-limit estimation (T4)",
        "question": "Estimate the human performance limit per event.",
        "unit": "event (leave-one-out stability)",
    },
    "transfer": {
        "primary_metric": "n_identified_pairs",
        "direction": "higher",
        "title": "Skill-transfer analysis (T5)",
        "question": "Identify causal skill-transfer pairs between events.",
        "unit": "event pair",
    },
}

TASK_NAMES = list(TASKS)

SOURCE_REPO_URL = f"https://github.com/{GITHUB_REPO}"
DATASET_URL = f"https://huggingface.co/datasets/{HF_DATASET_REPO}"
