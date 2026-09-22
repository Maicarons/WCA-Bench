"""Instrumental-variable skill transfer estimator (manual 2SLS)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from wca_bench.data.schema import EVENT_FORMATS


def _ols(dependent: np.ndarray, regressors: np.ndarray) -> np.ndarray:
    """Ordinary least squares coefficients via normal equations."""
    gram = regressors.T @ regressors
    gram = gram + 1e-8 * np.eye(gram.shape[0])
    return np.linalg.solve(gram, regressors.T @ dependent)


def iv_transfer_matrix(
    results: pd.DataFrame,
    *,
    min_pairs: int = 12,
    max_persons_per_pair: int = 400,
) -> dict[str, Any]:
    """Estimate a transfer matrix with a 2SLS instrumental-variable design.

    Instrument: whether a competitor's country hosted the source event before
    the competitor's own debut in that event (country-level availability of the
    event). Treatment: amount of source-event experience before the target-event
    debut. Outcome: log improvement in the target event after debut. The
    instrument is used to purge endogenous experience, and the slope from the
    second stage is the transfer estimate.
    """
    df = results.copy()
    if "date" not in df.columns:
        if "start_date" not in df.columns:
            return {"events": [], "matrix": [], "n_pairs": [], "method": "iv_2sls"}
        df["date"] = pd.to_datetime(df["start_date"])
    else:
        df["date"] = pd.to_datetime(df["date"])
    df = df[pd.to_numeric(df["best"], errors="coerce") > 0]
    if df.empty:
        return {"events": [], "matrix": [], "n_pairs": [], "method": "iv_2sls"}

    if "country_id" not in df.columns:
        df["country_id"] = "UNK"

    events = sorted(df["event_id"].astype(str).unique())
    idx = {e: i for i, e in enumerate(events)}
    n = len(events)
    matrix = np.full((n, n), np.nan)
    n_pairs = np.zeros((n, n), dtype=int)

    # country x event first hosting date (instrument relevance source)
    country_event_first = (
        df.assign(event_id=df["event_id"].astype(str))
        .groupby(["country_id", "event_id"])["date"]
        .min()
    )
    person_first = (
        df.assign(event_id=df["event_id"].astype(str))
        .groupby(["person_id", "event_id"])["date"]
        .min()
    )
    person_country = df.groupby("person_id")["country_id"].first()

    by_event = {
        e: g.sort_values(["person_id", "date"])
        for e, g in df.assign(event_id=df["event_id"].astype(str)).groupby("event_id")
    }

    for e_from in events:
        src = by_event.get(e_from)
        if src is None:
            continue
        for e_to in events:
            if e_from == e_to:
                matrix[idx[e_from], idx[e_to]] = 0.0
                continue
            dst = by_event.get(e_to)
            if dst is None:
                continue
            persons = []
            for pid, g in dst.groupby("person_id"):
                if len(g) < 2:
                    continue
                t0 = g["date"].min()
                post = g[g["date"] > t0]
                if len(post) < 1:
                    continue
                y = float(np.log(post["best"].iloc[:3].mean()) - np.log(g["best"].iloc[0]))
                src_hist = src[(src["person_id"] == pid) & (src["date"] < t0)]
                d = float(len(src_hist))
                pf = person_first.get((pid, e_from))
                if pf is None or pd.isna(pf):
                    continue
                country = person_country.get(pid, "UNK")
                host = country_event_first.get((country, e_from))
                z = 1.0 if (host is not None and not pd.isna(host) and host < pf) else 0.0
                persons.append((d, z, y))
                if len(persons) >= max_persons_per_pair:
                    break

            if len(persons) < min_pairs:
                n_pairs[idx[e_from], idx[e_to]] = len(persons)
                continue

            arr = np.asarray(persons, dtype=float)
            d = arr[:, 0]
            z = arr[:, 1]
            y = arr[:, 2]
            if np.std(z) < 1e-9 or np.std(d) < 1e-9:
                n_pairs[idx[e_from], idx[e_to]] = len(persons)
                continue

            z_mat = np.column_stack([np.ones_like(z), z])
            # first stage: treatment ~ instrument
            pi = _ols(d, z_mat)
            d_hat = z_mat @ pi
            x_hat = np.column_stack([np.ones_like(d_hat), d_hat])
            beta = _ols(y, x_hat)
            matrix[idx[e_from], idx[e_to]] = float(beta[1])
            n_pairs[idx[e_from], idx[e_to]] = len(persons)

    return {
        "events": events,
        "matrix": matrix.tolist(),
        "n_pairs": n_pairs.tolist(),
        "event_formats": {e: EVENT_FORMATS.get(e, {}).get("format", "time") for e in events},
        "method": "iv_2sls_country_event_availability",
        "note": "Instrument = country first-hosted source event before competitor debut; "
        "negative slope indicates later target performance improved.",
    }
