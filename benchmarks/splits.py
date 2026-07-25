"""Canonical and auditable benchmark splits."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


TRAIN_BUILDS = {
    "5.21.0.297",
    "5.22.0.289",
    "5.22.0.297",
    "5.22.0.301",
    "5.23.0.239",
    "5.23.0.250",
    "5.24.0.251",
    "5.24.0.254",
}
PIVOT_BUILD = "5.24.0.256"
LATE_BUILDS = {"5.24.0.259", "6.1.0.484"}
KNOWN_BUILDS = TRAIN_BUILDS | {PIVOT_BUILD} | LATE_BUILDS


def _hash_bucket(match_id: str) -> int:
    return int(hashlib.sha256(match_id.encode()).hexdigest()[:8], 16) % 100


def _validate_frame(frame: pd.DataFrame) -> None:
    required = {"match_id", "version", "row"}
    if not required <= set(frame.columns):
        raise ValueError(f"split frame missing columns: {sorted(required - set(frame.columns))}")
    unknown = set(frame["version"].dropna().unique()) - KNOWN_BUILDS
    if unknown:
        raise ValueError(f"unknown build(s) must be classified explicitly: {sorted(unknown)}")
    if frame["match_id"].astype(str).duplicated().any():
        raise ValueError("split frame contains duplicate match_id values")


def temporal_holdout_split(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    """Train on early builds and test on later builds using the documented proxy order."""
    _validate_frame(frame)
    train = frame["version"].isin(TRAIN_BUILDS)
    pivot = frame[frame["version"] == PIVOT_BUILD].sort_values(
        "match_id", key=lambda values: values.astype(np.int64)
    )
    n_val = int(len(pivot) * 0.2)
    val_ids = set(pivot["match_id"].iloc[:n_val])
    val = frame["match_id"].isin(val_ids)
    test = (
        ((frame["version"] == PIVOT_BUILD) & ~val)
        | frame["version"].isin(LATE_BUILDS)
    )
    result = {
        "train": frame.loc[train, "row"].to_numpy(),
        "val": frame.loc[val, "row"].to_numpy(),
        "test": frame.loc[test, "row"].to_numpy(),
    }
    _validate_partition(frame, result)
    return result


def iid_mixed_patch_split(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    """IID control with all builds represented in each split.

    This is intentionally not called ``same-patch``: it mixes all known builds.
    """
    _validate_frame(frame)
    bucket = frame["match_id"].astype(str).map(_hash_bucket)
    result = {
        "train": frame.loc[bucket < 80, "row"].to_numpy(),
        "val": frame.loc[(bucket >= 80) & (bucket < 90), "row"].to_numpy(),
        "test": frame.loc[bucket >= 90, "row"].to_numpy(),
    }
    _validate_partition(frame, result)
    return result


def same_build_split(frame: pd.DataFrame, build: str = PIVOT_BUILD) -> dict[str, np.ndarray]:
    """A genuine within-build 80/10/10 control."""
    _validate_frame(frame)
    subset = frame[frame["version"] == build]
    bucket = subset["match_id"].astype(str).map(_hash_bucket)
    result = {
        "train": subset.loc[bucket < 80, "row"].to_numpy(),
        "val": subset.loc[(bucket >= 80) & (bucket < 90), "row"].to_numpy(),
        "test": subset.loc[bucket >= 90, "row"].to_numpy(),
    }
    _validate_partition(subset, result)
    return result


def benchmark_splits(frame: pd.DataFrame) -> dict[str, dict[str, np.ndarray]]:
    return {
        "temporal-holdout": temporal_holdout_split(frame),
        "iid-mixed-patch": iid_mixed_patch_split(frame),
        f"same-build-{PIVOT_BUILD}": same_build_split(frame),
    }


def _validate_partition(frame: pd.DataFrame, split: dict[str, np.ndarray]) -> None:
    groups = [set(values.tolist()) for values in split.values()]
    if any(not group for group in groups):
        raise ValueError("train, val, and test must all be non-empty")
    if groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2]:
        raise ValueError("split partitions overlap")
    assigned = groups[0] | groups[1] | groups[2]
    expected = set(frame["row"].tolist())
    if assigned != expected:
        raise ValueError("split does not assign every row exactly once")


def write_split_manifest(
    frame: pd.DataFrame,
    settings: dict[str, dict[str, np.ndarray]],
    target: str | Path,
) -> Path:
    rows = frame.set_index("row")[["match_id", "version"]]
    records: list[dict] = []
    for setting, split in settings.items():
        for partition, indices in split.items():
            for index in indices:
                record = rows.loc[index]
                records.append(
                    {
                        "setting": setting,
                        "partition": partition,
                        "match_id": str(record["match_id"]),
                        "version": record["version"],
                    }
                )
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(path, index=False)
    return path
