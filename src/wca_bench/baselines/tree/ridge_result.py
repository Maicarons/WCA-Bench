"""Sklearn ridge / linear models for result prediction."""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLS = [
    "recent_mean",
    "recent_std",
    "recent_min",
    "recent_slope",
    "frozen_mean",
    "frozen_std",
    "frozen_best",
    "n_hist_valid",
    "n_competitions_hist",
    "historical_dnf_rate",
    "days_since_last",
]


def _prepare_matrix(df: pd.DataFrame):
    X = df[FEATURE_COLS].copy()
    for c in FEATURE_COLS:
        X[c] = pd.to_numeric(X[c], errors="coerce")
        med = np.nanmedian(X[c].to_numpy(dtype=float))
        if not np.isfinite(med):
            med = 0.0
        X[c] = X[c].fillna(med).to_numpy(dtype=float)
    return X.to_numpy(dtype=float)


def ridge_result_predict(task, alpha: float = 1.0) -> pd.DataFrame:
    """Ridge regression on frozen/recent stats → log(best)."""
    try:
        from sklearn.linear_model import Ridge
    except Exception as exc:
        raise RuntimeError(f"scikit-learn required for ridge baseline: {exc}") from exc

    train = task._train_features if hasattr(task, "_train_features") else None
    feats = task._features if hasattr(task, "_features") else task.featurize(None)
    if train is None or train.empty:
        # fit on features that have targets
        train = feats[feats.get("best", pd.Series(dtype=float)) > 0]
    train = train[train["best"].notna() & (train["best"] > 0)] if "best" in train.columns else train
    if train.empty:
        # fallback: identity on recent_mean
        preds = feats.copy()
        preds["y_pred"] = preds["recent_mean"]
        preds["y_true"] = preds.get("best")
        return preds

    y_train = np.log(train["best"].astype(float).to_numpy())
    X_train = _prepare_matrix(train)
    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)
    X_test = _prepare_matrix(feats)
    y_pred = np.exp(model.predict(X_test))

    out = feats.copy()
    out["y_pred"] = y_pred
    out["y_true"] = out["best"].astype(float).where(out["best"] > 0)
    out["y_true_avg"] = out["average"].astype(float).where(out["average"] > 0)
    out["y_pred_avg"] = y_pred
    return out
