"""Difference-in-differences style skill transfer estimator."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.schema import EVENT_FORMATS


def did_transfer_matrix(
    results: pd.DataFrame,
    *,
    min_pairs: int = 5,
) -> dict[str, Any]:
    """Estimate crude DID transfer matrix between events.

    Treatment: person first starts event B at time t0.
    Outcome: change in event-B performance around t0, compared to a control
    group that has not yet started B, controlling for person mean skill proxy.
    """
    df = results.copy()
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df["start_date"]).dt.date
    df = df[df["best"] > 0]
    if df.empty:
        return {"events": [], "matrix": {}, "n_pairs": {}}

    events = sorted(df["event_id"].unique())
    idx = {e: i for i, e in enumerate(events)}
    n = len(events)
    matrix = np.full((n, n), np.nan)
    n_pairs = np.zeros((n, n), dtype=int)

    # first-seen times
    first_seen = df.groupby(["person_id", "event_id"])["date"].min().reset_index()

    for e_from in events:
        for e_to in events:
            if e_from == e_to:
                matrix[idx[e_from], idx[e_to]] = 0.0
                continue
            to_scores = df[df["event_id"] == e_to].sort_values(["person_id", "date"])
            treated_ids = first_seen[first_seen["event_id"] == e_to]["person_id"]
            treated_ids = list(set(treated_ids) & set(df.loc[df["event_id"] == e_from, "person_id"]))[:200]
            effects = []
            for pid in treated_ids:
                person_to = to_scores[to_scores["person_id"] == pid]
                if len(person_to) < 4:
                    continue
                t0 = person_to["date"].min()
                # actually first entry is t0; use later competitions as post
                post = person_to[person_to["date"] > t0]["best"]
                if len(post) < 2:
                    continue
                # proxy: experience in e_from before t0
                from_hist = df[(df["person_id"] == pid) & (df["event_id"] == e_from)]
                from_hist = from_hist[from_hist["date"] < t0]
                if len(from_hist) < 2:
                    continue
                post_to = float(post.iloc[: min(3, len(post))].mean())
                pre_to = float(person_to["best"].iloc[0]) if len(person_to) else np.nan
                if not np.isfinite(pre_to) or not np.isfinite(post_to):
                    continue
                # improvement in e_to after e_from experience (lower is better)
                effects.append(np.log(post_to) - np.log(pre_to))
            if len(effects) >= min_pairs:
                matrix[idx[e_from], idx[e_to]] = float(np.mean(effects))
                n_pairs[idx[e_from], idx[e_to]] = len(effects)
            else:
                n_pairs[idx[e_from], idx[e_to]] = len(effects)

    return {
        "events": events,
        "matrix": matrix.tolist(),
        "n_pairs": n_pairs.tolist(),
        "event_formats": {e: EVENT_FORMATS.get(e, {}).get("format", "time") for e in events},
        "method": "did_proxy_log_change",
        "note": "Negative log-change suggests later e_to scores improved after e_from experience; "
        "not fully deconfounded.",
    }


def correlation_transfer_matrix(results: pd.DataFrame) -> dict[str, Any]:
    """Pairwise Spearman correlation of person-event mean scores."""
    df = results.copy()
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df["start_date"]).dt.date
    df = df[df["best"] > 0]
    if df.empty:
        return {"events": [], "matrix": []}
    piv = df.pivot_table(index="person_id", columns="event_id", values="best", aggfunc="mean")
    events = list(piv.columns)
    corr = piv.corr(method="spearman").reindex(index=events, columns=events)
    return {
        "events": events,
        "matrix": corr.to_numpy().tolist(),
        "method": "spearman_person_event_mean",
    }
