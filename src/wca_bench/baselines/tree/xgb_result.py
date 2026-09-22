"""XGBoost result prediction baseline (optional dependency, RF fallback)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.tree.ridge_result import _prepare_matrix
from wca_bench.utils.device import device_label, resolve_device


def _build_regressor(n_estimators: int, max_depth: int, device: str = "cpu"):
    """Return ``(model, backend, reason)``; reason is set when falling back to RF."""
    try:
        from xgboost import XGBRegressor
    except Exception as exc:
        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(
            n_estimators=max(n_estimators, 120),
            max_depth=max_depth,
            random_state=42,
            n_jobs=2,
        )
        return model, "random_forest", f"xgboost import failed: {type(exc).__name__}: {exc}"
    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=2,
        device=device,
    )
    return model, "xgboost", None


def xgb_result_predict(
    task,
    n_estimators: int = 80,
    max_depth: int = 4,
    device: str | None = None,
) -> pd.DataFrame:
    """Predict log(best) with gradient boosting, falling back to random forest.

    ``device`` defaults to CPU; ``"auto"``/``"cuda"`` requests GPU boosting when
    XGBoost and CUDA are available. If a CUDA fit fails the model is retrained on
    CPU and the reason is recorded in ``attrs`` (``fallback: cuda_failed``).
    """
    resolved = resolve_device(device if device is not None else getattr(task, "device", None))
    feats = task._features if hasattr(task, "_features") else task.featurize(None)
    train = getattr(task, "_train_features", None)
    if train is None or train.empty:
        train = feats
    train = train[train["best"].notna() & (train["best"] > 0)] if "best" in train.columns else train
    if train.empty:
        out = feats.copy()
        out["y_pred"] = out["recent_mean"]
        out["y_true"] = out.get("best")
        return out

    y_train = np.log(train["best"].astype(float).to_numpy())
    X_train = _prepare_matrix(train)
    xgb_device = "cuda" if resolved.startswith("cuda") else "cpu"
    model, backend, fallback_reason = _build_regressor(n_estimators, max_depth, xgb_device)
    try:
        model.fit(X_train, y_train)
    except Exception as exc:  # noqa: BLE001 - retry on CPU, reason is recorded
        if xgb_device == "cuda":
            fallback_reason = (
                f"xgboost cuda fit failed ({type(exc).__name__}: {exc}); retried on cpu"
            )
            model, backend, _ = _build_regressor(n_estimators, max_depth, "cpu")
            model.fit(X_train, y_train)
        else:
            raise

    y_pred = np.exp(model.predict(_prepare_matrix(feats)))
    out = feats.copy()
    out["y_pred"] = y_pred
    out["y_true"] = out["best"].astype(float).where(out["best"] > 0)
    out["y_true_avg"] = out["average"].astype(float).where(out["average"] > 0)
    out["y_pred_avg"] = y_pred
    out.attrs["backend"] = backend
    on_gpu = backend == "xgboost" and xgb_device == "cuda" and fallback_reason is None
    out.attrs["device"] = device_label(resolved) if on_gpu else "cpu"
    if backend != "xgboost":
        out.attrs["fallback"] = "no_xgboost"
    elif fallback_reason is not None:
        out.attrs["fallback"] = "cuda_failed"
    if fallback_reason is not None:
        out.attrs["fallback_reason"] = fallback_reason
    return out
