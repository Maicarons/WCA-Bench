"""Gradient-boosted / random-forest DNF probability baseline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.tree.ridge_result import _prepare_matrix
from wca_bench.utils.device import device_label, resolve_device
from wca_bench.utils.frame import numeric_column


def _build_classifier(n_estimators: int, max_depth: int, device: str = "cpu"):
    """Return ``(model, backend, reason)``; reason is set when falling back to RF."""
    try:
        from xgboost import XGBClassifier
    except Exception as exc:
        from sklearn.ensemble import RandomForestClassifier

        model = RandomForestClassifier(
            n_estimators=max(n_estimators, 120),
            max_depth=max_depth,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=2,
        )
        return model, "random_forest", f"xgboost import failed: {type(exc).__name__}: {exc}"
    model = XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
        n_jobs=2,
        device=device,
    )
    return model, "xgboost", None


def xgb_dnf_predict(
    task,
    n_estimators: int = 120,
    max_depth: int = 4,
    device: str | None = None,
) -> pd.DataFrame:
    """Predict per-result DNF probability from context features.

    Uses XGBoost when installed and falls back to
    ``sklearn.ensemble.RandomForestClassifier`` otherwise, so the baseline stays
    runnable in dependency-light CI environments. ``device`` defaults to CPU; a
    failed CUDA fit is retried on CPU with the reason recorded in ``attrs``.
    """
    resolved = resolve_device(device if device is not None else getattr(task, "device", None))
    feats = task._features if hasattr(task, "_features") and task._features is not None else task.featurize(None)
    feats = feats.copy() if isinstance(feats, pd.DataFrame) else pd.DataFrame()
    if feats.empty:
        return feats

    train = getattr(task, "_train_features", None)
    if train is None or (isinstance(train, pd.DataFrame) and train.empty):
        train = feats
    train = train.copy()
    if "target_dnf" not in train.columns:
        train["target_dnf"] = np.nan
    train = train[train["target_dnf"].notna()]

    global_rate = float(task.data.frozen_stats.get("global_dnf_rate", 0.03))
    hist = numeric_column(feats, "historical_dnf_rate").fillna(global_rate)

    if train.empty or train["target_dnf"].nunique() < 2:
        out = feats.copy()
        out["y_true"] = feats.get("target_dnf", pd.Series(np.nan, index=feats.index))
        out["y_pred"] = hist
        out["hard_uncertain"] = (hist >= 0.1) & (hist <= 0.3)
        out.attrs["device"] = "cpu"
        out.attrs["fallback"] = "single_class_history"
        return out

    xgb_device = "cuda" if resolved.startswith("cuda") else "cpu"
    model, backend, fallback_reason = _build_classifier(n_estimators, max_depth, xgb_device)
    y_train = train["target_dnf"].astype(int).to_numpy()
    X_train = _prepare_matrix(train)
    try:
        model.fit(X_train, y_train)
    except Exception as exc:  # noqa: BLE001 - retry on CPU, reason is recorded
        if xgb_device == "cuda":
            fallback_reason = (
                f"xgboost cuda fit failed ({type(exc).__name__}: {exc}); retried on cpu"
            )
            model, backend, _ = _build_classifier(n_estimators, max_depth, "cpu")
            model.fit(X_train, y_train)
        else:
            raise

    proba = model.predict_proba(_prepare_matrix(feats))[:, 1]
    out = feats.copy()
    out["y_true"] = feats.get("target_dnf", pd.Series(np.nan, index=feats.index))
    out["y_pred"] = proba
    out["hard_uncertain"] = (hist >= 0.1) & (hist <= 0.3)
    out.attrs["dnf_backend"] = backend
    on_gpu = backend == "xgboost" and xgb_device == "cuda" and fallback_reason is None
    out.attrs["device"] = device_label(resolved) if on_gpu else "cpu"
    if backend != "xgboost":
        out.attrs["fallback"] = "no_xgboost"
    elif fallback_reason is not None:
        out.attrs["fallback"] = "cuda_failed"
    if fallback_reason is not None:
        out.attrs["fallback_reason"] = fallback_reason
    return out
