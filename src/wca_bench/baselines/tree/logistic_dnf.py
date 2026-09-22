"""Logistic regression baseline for DNF prediction."""

from __future__ import annotations

import pandas as pd

from wca_bench.baselines.tree.ridge_result import _prepare_matrix


def logistic_dnf_predict(task) -> pd.DataFrame:
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception as exc:
        raise RuntimeError(f"scikit-learn required: {exc}") from exc

    feats = task._features if hasattr(task, "_features") else task.featurize(None)
    train = getattr(task, "_train_features", None)
    if train is None or train.empty:
        train = feats
    train = train[train["target_dnf"].notna()].copy() if "target_dnf" in train.columns else train
    if train.empty or train["target_dnf"].nunique() < 2:
        # fallback to historical rate
        out = feats.copy()
        out["y_true"] = out.get("target_dnf")
        out["y_pred"] = out.get("historical_dnf_rate", 0.03)
        return out

    X_train = _prepare_matrix(train)
    y_train = train["target_dnf"].astype(int).to_numpy()
    model = LogisticRegression(max_iter=500, class_weight="balanced")
    model.fit(X_train, y_train)
    proba = model.predict_proba(_prepare_matrix(feats))[:, 1]
    out = feats.copy()
    out["y_true"] = out.get("target_dnf")
    out["y_pred"] = proba
    out["hard_uncertain"] = (out.get("historical_dnf_rate", pd.Series(dtype=float)).fillna(0) >= 0.1) & (
        out.get("historical_dnf_rate", pd.Series(dtype=float)).fillna(1) <= 0.3
    )
    return out
