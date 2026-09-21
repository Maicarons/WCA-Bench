"""XGBoost result prediction baseline (optional dependency)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.tree.ridge_result import FEATURE_COLS, _prepare_matrix


def xgb_result_predict(task, n_estimators: int = 80, max_depth: int = 4) -> pd.DataFrame:
    try:
        from xgboost import XGBRegressor
    except Exception as exc:
        raise RuntimeError(f"xgboost required: {exc}") from exc

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
    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=2,
    )
    model.fit(X_train, y_train)
    y_pred = np.exp(model.predict(_prepare_matrix(feats)))
    out = feats.copy()
    out["y_pred"] = y_pred
    out["y_true"] = out["best"].astype(float).where(out["best"] > 0)
    out["y_true_avg"] = out["average"].astype(float).where(out["average"] > 0)
    out["y_pred_avg"] = y_pred
    return out
