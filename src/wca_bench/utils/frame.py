"""Typed helpers for DataFrame column access.

``pandas-stubs`` models ``DataFrame.get`` as returning ``Series | None``, which
makes ``pd.to_numeric`` overload resolution ambiguous. :func:`numeric_column`
centralises the safe pattern: coerce the column to float, and treat a missing
column as an all-NaN column so the ``fillna`` defaults in the baselines keep
working instead of raising.
"""

from __future__ import annotations

from typing import cast

import numpy as np
import pandas as pd


def numeric_column(df: pd.DataFrame, name: str) -> pd.Series:
    """Return ``df[name]`` coerced to a float Series.

    A missing column yields an all-NaN Series aligned to ``df.index`` rather than
    raising, so callers that immediately apply ``fillna`` keep their intended
    fallback value.
    """
    if name not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype=float)
    return pd.to_numeric(cast("pd.Series", df[name]), errors="coerce")
