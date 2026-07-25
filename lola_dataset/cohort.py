"""Shared cohort rules for all LoLA-2016 benchmarks and analyses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import SHORT_MATCH_MINUTES


def eligible_matches(
    parquet_dir: str | Path, min_duration: int = SHORT_MATCH_MINUTES
) -> pd.DataFrame:
    """Return the canonical eligible match frame.

    Every downstream analysis must start from this frame rather than silently
    defining its own duration filter.
    """
    path = Path(parquet_dir) / "matches.parquet"
    matches = pd.read_parquet(path, columns=["match_id", "version", "duration"])
    matches["match_id"] = matches["match_id"].astype(str)
    eligible = matches[matches["duration"] >= min_duration].copy()
    if eligible["match_id"].duplicated().any():
        raise ValueError("matches.parquet contains duplicate match_id values")
    return eligible.sort_values("match_id").reset_index(drop=True)


def filter_to_eligible(frame: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Filter a frame to the canonical cohort and normalize match IDs."""
    result = frame.copy()
    result["match_id"] = result["match_id"].astype(str)
    return result[result["match_id"].isin(set(matches["match_id"]))].copy()
