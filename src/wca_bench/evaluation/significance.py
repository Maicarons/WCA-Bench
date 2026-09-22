"""Statistical significance tests and effect sizes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from scipy import stats


def bootstrap_ci(
    values,
    metric_fn: Callable[[np.ndarray], float],
    n_boot: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict[str, Any]:
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return {"point": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    rng = np.random.default_rng(seed)
    stats_list = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample = rng.choice(vals, size=len(vals), replace=True)
        stats_list[i] = metric_fn(sample)
    lo, hi = np.percentile(stats_list, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {
        "point": float(metric_fn(vals)),
        "lo": float(lo),
        "hi": float(hi),
        "n": int(len(vals)),
        "n_boot": n_boot,
        "alpha": alpha,
        "seed": seed,
    }


def paired_t_test(
    errors_a,
    errors_b,
    *,
    comparison: str = "A vs B",
    task: str = "unknown",
    metric: str = "error",
    paired_unit: str = "competition_event_round",
) -> dict[str, Any]:
    a = np.asarray(errors_a, dtype=float)
    b = np.asarray(errors_b, dtype=float)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    if len(a) < 2:
        return {
            "comparison": comparison,
            "task": task,
            "metric": metric,
            "paired_unit": paired_unit,
            "n_pairs": int(len(a)),
            "mean_diff": float("nan"),
            "p_value": float("nan"),
        }
    stat, p = stats.ttest_rel(a, b)
    diff = a - b
    from wca_bench.evaluation.metrics import cliffs_delta, cohens_d
    from wca_bench.evaluation.significance import bootstrap_ci as _bci

    ci = _bci(diff, lambda x: float(np.mean(x)), n_boot=1000, seed=42)
    return {
        "comparison": comparison,
        "task": task,
        "metric": metric,
        "paired_unit": paired_unit,
        "n_pairs": int(len(a)),
        "mean_diff": float(np.mean(diff)),
        "ci95": [ci["lo"], ci["hi"]],
        "p_value": float(p),
        "effect_size": {
            "name": "cohens_d",
            "value": cohens_d(a, b),
            "cliffs_delta": cliffs_delta(a, b),
        },
        "test": "paired_t",
        "seed": 42,
        "t_stat": float(stat),
    }


def friedman_nemenyi(
    score_matrix: np.ndarray,
    model_names: list[str],
    *,
    task: str = "unknown",
    metric: str = "score",
) -> dict[str, Any]:
    """score_matrix shape: (n_datasets, n_models), higher is better after rank conversion.

    We rank within each dataset (1=best) then apply Friedman + Nemenyi critical difference.
    """
    X = np.asarray(score_matrix, dtype=float)
    if X.ndim != 2:
        raise ValueError("score_matrix must be 2D (n_datasets x n_models)")
    n_datasets, k = X.shape
    if k < 2 or n_datasets < 2:
        return {"error": "need >=2 datasets and >=2 models", "task": task}

    ranks = np.zeros_like(X)
    for i in range(n_datasets):
        ranks[i] = stats.rankdata(-X[i], method="average")  # higher score -> rank 1
    mean_ranks = ranks.mean(axis=0)
    # Friedman
    try:
        chi2, p = stats.friedmanchisquare(*[X[:, j] for j in range(k)])
        friedman_p = float(p)
        friedman_chi2 = float(chi2)
    except Exception:
        friedman_p = float("nan")
        friedman_chi2 = float("nan")

    # Nemenyi critical difference (alpha=0.05)
    q_alpha = {2: 1.960, 3: 2.344, 4: 2.569, 5: 2.728, 6: 2.850}.get(k, 2.9)
    cd = q_alpha * np.sqrt(k * (k + 1) / (6.0 * n_datasets))

    comparisons = []
    for i in range(k):
        for j in range(i + 1, k):
            diff = abs(mean_ranks[i] - mean_ranks[j])
            comparisons.append(
                {
                    "a": model_names[i],
                    "b": model_names[j],
                    "rank_diff": float(diff),
                    "significant": bool(diff > cd),
                }
            )

    return {
        "task": task,
        "metric": metric,
        "n_datasets": int(n_datasets),
        "models": model_names,
        "mean_ranks": {model_names[j]: float(mean_ranks[j]) for j in range(k)},
        "friedman_chi2": friedman_chi2,
        "friedman_p": friedman_p,
        "critical_difference": float(cd),
        "comparisons": comparisons,
    }
