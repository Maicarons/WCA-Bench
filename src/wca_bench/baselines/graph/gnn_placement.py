"""Heterogeneous person-competition graph neural network for placement.

A tiny 2-layer mean-aggregation GNN is trained with ``torch`` when available.
Without torch (or if training fails) the baseline falls back to pure-numpy graph
propagation features combined with a Plackett-Luce style ranking, recording
``fallback: no_torch`` in the prediction ``attrs``.

The default device is **CPU**: per-competition placement scoring is
latency-sensitive and the working set is small (2k–80k rows), so CPU is usually
faster than GPU; ``device="auto"`` opts into CUDA when available.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from wca_bench.baselines.statistical.plackett_luce import psych_sheet_predict
from wca_bench.utils.device import device_label, resolve_device


def _train_frame(task) -> pd.DataFrame:
    train = getattr(task, "_train_features", None)
    if train is None or not isinstance(train, pd.DataFrame) or train.empty:
        train = task.data.results
    return train


def _person_skill(train: pd.DataFrame) -> pd.Series:
    df = train.copy()
    df = df[pd.to_numeric(df["best"], errors="coerce") > 0]
    if df.empty:
        return pd.Series(dtype=float)
    df["log_best"] = np.log(df["best"].astype(float))
    return -df.groupby("person_id")["log_best"].mean()


def _numpy_graph_adjust(task, base: pd.DataFrame, gamma: float = 0.25) -> pd.Series:
    """Propagated graph skill signal used for the no-torch fallback."""
    train = _train_frame(task)
    if train.empty or "person_id" not in train.columns:
        return pd.Series(1.0, index=base.index)
    skill = _person_skill(train)
    if skill.empty:
        return pd.Series(1.0, index=base.index)
    sk = pd.to_numeric(skill, errors="coerce")
    sk = (sk - sk.mean()) / (sk.std() or 1.0)
    comp_quality = train.assign(_sk=train["person_id"].map(sk)).groupby("competition_id")["_sk"].mean()
    person_prop = (
        train.assign(_q=train["competition_id"].map(comp_quality))
        .groupby("person_id")["_q"]
        .mean()
    )
    z = pd.to_numeric(base["person_id"].map(person_prop), errors="coerce").fillna(0.0)
    z = (z - z.mean()) / (z.std() or 1.0)
    return pd.Series(np.exp(-gamma * z.to_numpy()), index=z.index)


COV_COLS = ["recent_mean", "recent_std", "frozen_mean", "n_hist_valid"]


def _covariates(df: pd.DataFrame) -> np.ndarray:
    """Return a fixed-width (n, 4) covariate matrix, zero-filling missing cols."""
    out = np.zeros((len(df), len(COV_COLS)), dtype=float)
    for j, col in enumerate(COV_COLS):
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            med = s.median()
            out[:, j] = s.fillna(med if np.isfinite(med) else 0.0).to_numpy(dtype=float)
    return out


def _torch_graph_adjust(task, base: pd.DataFrame, train: pd.DataFrame, device: str = "cpu", epochs: int = 3):
    import torch
    from torch import nn

    dev = torch.device(device)
    tr = train[train["best"].notna() & (pd.to_numeric(train["best"], errors="coerce") > 0)].copy()
    if len(tr) < 64:
        return None
    tr = tr.sample(n=min(len(tr), 20000), random_state=42) if len(tr) > 20000 else tr
    persons = pd.Index(pd.concat([tr["person_id"], base["person_id"]]).astype(str).unique())
    comps = pd.Index(pd.concat([tr["competition_id"], base["competition_id"]]).astype(str).unique())
    p_map = {p: i for i, p in enumerate(persons)}
    c_map = {c: i for i, c in enumerate(comps)}

    tr_edges = np.column_stack(
        [tr["person_id"].astype(str).map(p_map), tr["competition_id"].astype(str).map(c_map)]
    ).astype(np.int64)
    cov = _covariates(tr)
    y = np.log(tr["best"].astype(float).to_numpy())
    mu, sd = float(y.mean()), float(y.std() or 1.0)
    y_n = (y - mu) / sd

    edge_c = torch.tensor(tr_edges[:, 1], device=dev)
    edge_p = torch.tensor(tr_edges[:, 0], device=dev)
    ones_e = torch.ones(len(tr_edges), device=dev)
    dim = 16

    class GNN(nn.Module):
        def __init__(self, n_p: int, n_c: int) -> None:
            super().__init__()
            self.p_emb = nn.Embedding(n_p, dim)
            self.c_emb = nn.Embedding(n_c, dim)
            self.c_lin = nn.Linear(dim * 2, dim)
            self.p_lin = nn.Linear(dim * 2, dim)
            self.head = nn.Sequential(nn.Linear(dim * 2 + 4, 32), nn.ReLU(), nn.Linear(32, 1))

        def propagate(self):
            h_p = self.p_emb.weight
            h_c = self.c_emb.weight
            for _ in range(2):
                agg_c = torch.zeros_like(h_c).index_add_(0, edge_c, h_p[edge_p])
                cnt_c = torch.zeros(h_c.shape[0], device=dev).index_add_(0, edge_c, ones_e).clamp(min=1).unsqueeze(-1)
                h_c = torch.relu(self.c_lin(torch.cat([h_c, agg_c / cnt_c], dim=-1)))
                agg_p = torch.zeros_like(h_p).index_add_(0, edge_p, h_c[edge_c])
                cnt_p = torch.zeros(h_p.shape[0], device=dev).index_add_(0, edge_p, ones_e).clamp(min=1).unsqueeze(-1)
                h_p = torch.relu(self.p_lin(torch.cat([h_p, agg_p / cnt_p], dim=-1)))
            return h_p, h_c

    torch.manual_seed(42)
    model = GNN(len(persons), len(comps)).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=5e-3)
    loss_fn = nn.MSELoss()
    p_idx = edge_p
    c_idx = edge_c
    xt = torch.tensor(cov, dtype=torch.float32, device=dev)
    yt = torch.tensor(y_n, dtype=torch.float32, device=dev)
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        h_p, h_c = model.propagate()
        pred = model.head(torch.cat([h_p[p_idx], h_c[c_idx], xt], dim=-1)).squeeze(-1)
        loss = loss_fn(pred, yt)
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        h_p, h_c = model.propagate()
        bp = torch.tensor(
            base["person_id"].astype(str).map(p_map).fillna(0).astype(int).to_numpy(), device=dev
        )
        bc = torch.tensor(
            base["competition_id"].astype(str).map(c_map).fillna(0).astype(int).to_numpy(), device=dev
        )
        cov_b = _covariates(base)
        out = model.head(
            torch.cat([h_p[bp], h_c[bc], torch.tensor(cov_b, dtype=torch.float32, device=dev)], dim=-1)
        )
        pred_log = out.squeeze(-1).detach().cpu().numpy() * sd + mu
    return np.exp(np.clip(pred_log, -30.0, 30.0))


def _rerank(out: pd.DataFrame) -> pd.DataFrame:
    gcols = [c for c in ["competition_id", "event_id", "round_type_id"] if c in out.columns]
    if not gcols:
        gcols = ["competition_id"]
    res = out.copy()
    res["y_pred_rank"] = res.groupby(gcols)["y_pred"].rank(ascending=True, method="average")
    if "y_true" in res.columns:
        res["y_true_rank"] = res.groupby(gcols)["y_true"].rank(ascending=True, method="average")
    res["p_podium"] = (res["y_pred_rank"] <= 3).astype(float)
    return res


def gnn_placement_predict(task, device: str | None = None) -> pd.DataFrame:
    """Person-competition heterogeneous GNN for placement (torch optional).

    ``device`` defaults to CPU for reproducibility; pass ``"auto"`` to use CUDA
    when available.
    """
    base = psych_sheet_predict(task)
    if base.empty:
        return base

    train = _train_frame(task)
    resolved = resolve_device(device if device is not None else getattr(task, "device", None))
    label = device_label(resolved)
    fallback = False
    backend = "gnn"
    factor = None
    torch_error: str | None = None
    if "person_id" in base.columns and "competition_id" in base.columns:
        try:
            import torch  # noqa: F401

            factor = _torch_graph_adjust(task, base, train, resolved)
        except ImportError as exc:
            torch_error = f"ImportError: {exc}"
            factor = None
        except Exception as exc:  # noqa: BLE001 - reported in attrs, never swallowed silently
            torch_error = f"{type(exc).__name__}: {exc}"
            factor = None
    if factor is None or not np.isfinite(factor).any():
        fallback = True
        backend = "numpy_graph_propagation"
        label = "cpu"
        factor = _numpy_graph_adjust(task, base)

    out = base.copy()
    out["y_pred"] = pd.to_numeric(out["y_pred"], errors="coerce").to_numpy() * np.asarray(factor)
    out = _rerank(out)
    out.attrs["backend"] = backend
    out.attrs["device"] = label
    if label.startswith("cuda"):
        out.attrs["gpu_model"] = label.split(":", 1)[-1]
    if fallback:
        out.attrs["fallback"] = "no_torch" if torch_error is None else "torch_error"
        if torch_error is not None:
            out.attrs["torch_error"] = torch_error
    return out
