"""Metric implementations for WCA-Bench tasks."""

from __future__ import annotations

import numpy as np


def _clean(y_true, y_pred, *, drop_nonfinite: bool = False):
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    if len(yt) != len(yp):
        raise ValueError("length mismatch")
    if drop_nonfinite:
        mask = np.isfinite(yt) & np.isfinite(yp)
        return yt[mask], yp[mask]
    return yt, yp


def mae(y_true, y_pred) -> float:
    yt, yp = _clean(y_true, y_pred, drop_nonfinite=True)
    if len(yt) == 0:
        return float("nan")
    return float(np.mean(np.abs(yt - yp)))


def rmse(y_true, y_pred) -> float:
    yt, yp = _clean(y_true, y_pred, drop_nonfinite=True)
    if len(yt) == 0:
        return float("nan")
    return float(np.sqrt(np.mean((yt - yp) ** 2)))


def mse(y_true, y_pred) -> float:
    yt, yp = _clean(y_true, y_pred, drop_nonfinite=True)
    if len(yt) == 0:
        return float("nan")
    return float(np.mean((yt - yp) ** 2))


def mae_log(y_true, y_pred) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(yp) & (yt > 0) & (yp > 0)
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs(np.log(yt[mask]) - np.log(yp[mask]))))


def rmse_log(y_true, y_pred) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(yp) & (yt > 0) & (yp > 0)
    if mask.sum() == 0:
        return float("nan")
    return float(np.sqrt(np.mean((np.log(yt[mask]) - np.log(yp[mask])) ** 2)))


def coverage(y_true, lower, upper) -> float:
    """Empirical coverage of prediction intervals."""
    yt, lo = _clean(y_true, lower, drop_nonfinite=True)
    yt2, hi = _clean(y_true, upper, drop_nonfinite=True)
    n = min(len(yt), len(hi))
    if n == 0:
        return float("nan")
    yt = np.asarray(y_true, dtype=float)[:n]
    lo = np.asarray(lower, dtype=float)[:n]
    hi = np.asarray(upper, dtype=float)[:n]
    mask = np.isfinite(yt) & np.isfinite(lo) & np.isfinite(hi)
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean((yt[mask] >= lo[mask]) & (yt[mask] <= hi[mask])))


def calibration_error(y_true, y_prob, n_bins: int = 10) -> float:
    """Expected calibration error for binary probabilities."""
    yt = np.asarray(y_true, dtype=float)
    yp = np.clip(np.asarray(y_prob, dtype=float), 0, 1)
    mask = np.isfinite(yt) & np.isfinite(yp)
    yt, yp = yt[mask], yp[mask]
    if len(yt) == 0:
        return float("nan")
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        sel = (yp >= bins[i]) & (yp < bins[i + 1] if i < n_bins - 1 else yp <= bins[i + 1])
        if sel.sum() == 0:
            continue
        ece += abs(yt[sel].mean() - yp[sel].mean()) * (sel.sum() / len(yt))
    return float(ece)


def kendall_tau(y_true_rank, y_pred_rank) -> float:
    """Kendall tau-b between true and predicted ranks."""
    try:
        from scipy.stats import kendalltau

        a = np.asarray(y_true_rank, dtype=float)
        b = np.asarray(y_pred_rank, dtype=float)
        mask = np.isfinite(a) & np.isfinite(b)
        if mask.sum() < 2:
            return float("nan")
        tau, _ = kendalltau(a[mask], b[mask])
        return float(tau)
    except Exception:
        # fallback O(n^2) concordance
        a = np.asarray(y_true_rank, dtype=float)
        b = np.asarray(y_pred_rank, dtype=float)
        mask = np.isfinite(a) & np.isfinite(b)
        a, b = a[mask], b[mask]
        n = len(a)
        if n < 2:
            return float("nan")
        conc = disc = 0
        for i in range(n):
            for j in range(i + 1, n):
                s1 = np.sign(a[i] - a[j])
                s2 = np.sign(b[i] - b[j])
                if s1 == 0 or s2 == 0:
                    continue
                if s1 == s2:
                    conc += 1
                else:
                    disc += 1
        denom = conc + disc
        return float((conc - disc) / denom) if denom else float("nan")


def topk_accuracy(y_true_best, y_pred_rank, k: int = 3) -> float:
    """Fraction of rounds where predicted top-k set matches true top-k set membership overlap/k."""
    import pandas as pd

    df = pd.DataFrame({"true": y_true_best, "pred_rank": y_pred_rank})
    df = df.dropna()
    if df.empty:
        return float("nan")
    # true top-k are the k smallest true bests
    true_top = set(df.nsmallest(k, "true").index)
    pred_top = set(df.nsmallest(k, "pred_rank").index)
    return float(len(true_top & pred_top) / k)


def podium_overlap(y_true_best, y_pred_rank, k: int = 3) -> float:
    return topk_accuracy(y_true_best, y_pred_rank, k=k)


def brier_score(y_true_binary, y_prob) -> float:
    yt = np.asarray(y_true_binary, dtype=float)
    yp = np.asarray(y_prob, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(yp)
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean((yt[mask] - yp[mask]) ** 2))


def _rankdata(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(1, len(a) + 1)
    # average ties
    uniq, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
    if np.any(counts > 1):
        cum = 0
        avg = []
        for c in counts:
            avg.append((cum + 1 + cum + c) / 2.0)
            cum += c
        ranks = np.array(avg, dtype=float)[inv]
    return ranks


def auc_roc(y_true, y_score) -> float:
    yt = np.asarray(y_true, dtype=float)
    ys = np.asarray(y_score, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(ys)
    yt, ys = yt[mask], ys[mask]
    pos = (yt == 1).sum()
    neg = (yt == 0).sum()
    if pos == 0 or neg == 0:
        return float("nan")
    # Mann-Whitney U / AUC
    ranks = _rankdata(ys)
    sum_pos = ranks[yt == 1].sum()
    auc = (sum_pos - pos * (pos + 1) / 2) / (pos * neg)
    return float(auc)


def auc_pr(y_true, y_score) -> float:
    yt = np.asarray(y_true, dtype=float)
    ys = np.asarray(y_score, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(ys)
    yt, ys = yt[mask], ys[mask]
    pos = int((yt == 1).sum())
    if pos == 0:
        return float("nan")
    order = np.argsort(-ys)
    yt = yt[order]
    tp = np.cumsum(yt == 1)
    fp = np.cumsum(yt == 0)
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / pos
    # step-wise AP
    ap = 0.0
    prev_r = 0.0
    for p, r in zip(precision, recall, strict=False):
        ap += p * max(r - prev_r, 0)
        prev_r = r
    return float(ap)


def f1(y_true, y_pred, threshold: float = 0.5) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    if yp.dtype != bool and (np.nanmax(yp) <= 1.0 if np.isfinite(yp).any() else False):
        yp = yp >= threshold
    tp = float(np.sum((yt == 1) & (yp == 1)))
    fp = float(np.sum((yt == 0) & (yp == 1)))
    fn = float(np.sum((yt == 1) & (yp == 0)))
    denom = 2 * tp + fp + fn
    return float(2 * tp / denom) if denom else float("nan")


def matthews_corrcoef(y_true, y_pred, threshold: float = 0.5) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    if yp.dtype != bool and np.isfinite(yp).any() and np.nanmax(yp) <= 1.0:
        yp = yp >= threshold
    tp = float(np.sum((yt == 1) & (yp == 1)))
    tn = float(np.sum((yt == 0) & (yp == 0)))
    fp = float(np.sum((yt == 0) & (yp == 1)))
    fn = float(np.sum((yt == 1) & (yp == 0)))
    denom = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return float((tp * tn - fp * fn) / denom) if denom else float("nan")


def cohens_d(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    na, nb = len(a), len(b)
    sa, sb = a.std(ddof=1), b.std(ddof=1)
    pooled = np.sqrt(((na - 1) * sa**2 + (nb - 1) * sb**2) / (na + nb - 2))
    if pooled == 0:
        return 0.0
    return float((a.mean() - b.mean()) / pooled)


def cliffs_delta(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    gt = 0
    lt = 0
    for x in a:
        gt += np.sum(x > b)
        lt += np.sum(x < b)
    n = len(a) * len(b)
    return float((gt - lt) / n)
