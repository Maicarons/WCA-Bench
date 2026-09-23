"""Sequence model (LSTM) for result prediction with an optional torch dependency.

When ``torch`` is unavailable (or training fails) the baseline degrades to a
sliding-window ridge model over recent person-event statistics and records
``fallback: no_torch`` in the prediction ``attrs``.

The default device is **CPU**: WCA-Bench preprocessing runs on small batches
(2k–80k rows, per-competition forward passes) and is latency-sensitive, so CPU
usually wins; ``device="auto"`` (or ``WCA_BENCH_DEVICE=cuda``) opts into GPU.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.history_mean import history_mean_predict
from wca_bench.utils.device import device_label, resolve_device
from wca_bench.utils.frame import numeric_column

SEQ_COLS = ["recent_mean", "recent_std", "recent_min", "recent_slope", "frozen_mean", "frozen_std"]


def _clean_matrix(df: pd.DataFrame) -> np.ndarray:
    cols = [c for c in SEQ_COLS if c in df.columns]
    x = df[cols].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float).copy()
    med = np.nanmedian(x, axis=0) if len(x) else np.zeros(len(cols))
    med = np.where(np.isfinite(med), med, 0.0)
    idx = np.where(~np.isfinite(x))
    if len(idx[0]):
        x[idx] = med[idx[1]]
    return x


def _fallback_ridge(task, feats: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    from sklearn.linear_model import Ridge

    if train.empty or "best" not in train.columns:
        return numeric_column(feats, "recent_mean").to_numpy(dtype=float)
    tr = train[train["best"].notna() & (train["best"] > 0)]
    if tr.empty:
        return numeric_column(feats, "recent_mean").to_numpy(dtype=float)
    model = Ridge(alpha=1.0)
    model.fit(_clean_matrix(tr), np.log(tr["best"].astype(float).to_numpy()))
    return np.exp(model.predict(_clean_matrix(feats)))


def _build_windows(
    df: pd.DataFrame, w: int, cap: int, min_context: int = 3
) -> tuple[np.ndarray, np.ndarray]:
    """Build (context, next-value) windows, left-padding short histories.

    Histories shorter than ``w`` are still usable: once a person-event has at
    least ``min_context`` rounds we left-pad the context to length ``w`` so the
    LSTM can train on modest datasets (e.g. synthetic CI runs).
    """
    d = df[df["best"].notna() & (df["best"] > 0)].copy()
    if d.empty or "date" not in d.columns:
        return np.empty((0, w)), np.empty((0,))
    d = d.sort_values(["person_id", "event_id", "date"])
    xs: list[np.ndarray] = []
    ys: list[float] = []
    for _, g in d.groupby(["person_id", "event_id"], sort=False):
        vals = np.log(g["best"].astype(float).to_numpy())
        if len(vals) <= min_context:
            continue
        for i in range(min_context, len(vals)):
            ctx = vals[max(0, i - w) : i]
            if len(ctx) < w:
                ctx = np.concatenate([np.full(w - len(ctx), float(ctx.mean())), ctx])
            xs.append(ctx)
            ys.append(float(vals[i]))
            if len(xs) >= cap:
                break
        if len(xs) >= cap:
            break
    if not xs:
        return np.empty((0, w)), np.empty((0,))
    return np.asarray(xs), np.asarray(ys)


def _last_windows(df: pd.DataFrame, w: int) -> dict[tuple[str, str], np.ndarray]:
    out: dict[tuple[str, str], np.ndarray] = {}
    if df.empty or "best" not in df.columns:
        return out
    d = df[df["best"].notna() & (df["best"] > 0)].sort_values(["person_id", "event_id", "date"])
    for (pid, eid), g in d.groupby(["person_id", "event_id"], sort=False):
        vals = np.log(g["best"].astype(float).to_numpy())
        out[(str(pid), str(eid))] = vals[-w:]
    return out


def _torch_predict(task, feats: pd.DataFrame, train: pd.DataFrame, w: int, cap: int, device: str):
    import torch
    from torch import nn

    dev = torch.device(device)
    tr = train if not train.empty else feats
    xs, ys = _build_windows(tr, w, cap)
    if len(xs) < 32:
        return None
    mu, sd = float(ys.mean()), float(ys.std() or 1.0)
    xs_n = (xs - mu) / sd
    ys_n = (ys - mu) / sd

    class LSTMReg(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.lstm = nn.LSTM(input_size=1, hidden_size=24, batch_first=True)
            self.head = nn.Linear(24, 1)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.head(out[:, -1, :]).squeeze(-1)

    torch.manual_seed(42)
    model = LSTMReg().to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=5e-3)
    loss_fn = nn.MSELoss()
    xt = torch.tensor(xs_n, dtype=torch.float32, device=dev).unsqueeze(-1)
    yt = torch.tensor(ys_n, dtype=torch.float32, device=dev)
    model.train()
    for _ in range(3):
        opt.zero_grad()
        loss = loss_fn(model(xt), yt)
        loss.backward()
        opt.step()

    windows = _last_windows(pd.concat([tr, feats], ignore_index=True), w)
    preds = []
    model.eval()
    with torch.no_grad():
        for _, row in feats.iterrows():
            key = (str(row.get("person_id")), str(row.get("event_id")))
            seq = windows.get(key)
            if seq is None or len(seq) == 0:
                preds.append(np.nan)
                continue
            padded = np.zeros(w, dtype=float)
            padded[-min(w, len(seq)) :] = seq[-w:]
            padded = np.where(padded == 0, mu, padded)
            tn = torch.tensor(
                ((padded - mu) / sd), dtype=torch.float32, device=dev
            ).view(1, w, 1)
            preds.append(float(model(tn).item()) * sd + mu)
    return np.exp(np.asarray(preds, dtype=float))


def lstm_result_predict(task, window: int = 8, cap: int = 20000, device: str | None = None) -> pd.DataFrame:
    """LSTM over recent person-event score sequences (torch optional).

    ``device`` defaults to CPU for reproducibility; pass ``"auto"`` to use CUDA
    when available.
    """
    feats = task._features if hasattr(task, "_features") and task._features is not None else task.featurize(None)
    feats = feats.copy() if isinstance(feats, pd.DataFrame) else pd.DataFrame()
    if feats.empty:
        return feats
    train = getattr(task, "_train_features", None)
    if train is None:
        train = pd.DataFrame()

    resolved = resolve_device(device if device is not None else getattr(task, "device", None))
    label = device_label(resolved)

    fallback = False
    y_pred = None
    backend = "lstm"
    torch_error: str | None = None
    try:
        import torch  # noqa: F401

        y_pred = _torch_predict(task, feats, train, window, cap, resolved)
    except ImportError as exc:
        torch_error = f"ImportError: {exc}"
        y_pred = None
    except Exception as exc:  # noqa: BLE001 - reported in attrs, never swallowed silently
        torch_error = f"{type(exc).__name__}: {exc}"
        y_pred = None

    if y_pred is None or not np.isfinite(y_pred).any():
        fallback = True
        backend = "sliding_window_ridge"
        label = "cpu"
        y_pred = _fallback_ridge(task, feats, train)

    base = history_mean_predict(task)
    out = base.copy()
    tmp = pd.DataFrame({"result_id": feats.get("result_id"), "y_pred": y_pred})
    if "result_id" in out.columns and tmp["result_id"].notna().any():
        out = out.merge(tmp, on="result_id", how="left", suffixes=("", "_lstm"))
        out["y_pred"] = out["y_pred_lstm"].fillna(out["y_pred"])
        out = out.drop(columns=[c for c in ["y_pred_lstm"] if c in out.columns])
    else:
        out["y_pred"] = pd.Series(y_pred, index=out.index)
    out.attrs["backend"] = backend
    out.attrs["device"] = label
    if label.startswith("cuda"):
        out.attrs["gpu_model"] = label.split(":", 1)[-1]
    if fallback:
        out.attrs["fallback"] = "no_torch" if torch_error is None else "torch_error"
        if torch_error is not None:
            out.attrs["torch_error"] = torch_error
    return out
