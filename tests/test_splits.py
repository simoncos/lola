from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from benchmarks.splits import (
    KNOWN_BUILDS,
    PIVOT_BUILD,
    benchmark_splits,
    temporal_holdout_split,
)


def make_frame() -> pd.DataFrame:
    records = []
    match_id = 2_000_000_000
    for build in sorted(KNOWN_BUILDS):
        count = 120 if build == PIVOT_BUILD else 20
        for _ in range(count):
            records.append({"match_id": str(match_id), "version": build})
            match_id += 1
    frame = pd.DataFrame(records)
    return frame.assign(row=np.arange(len(frame)))


class SplitContractTests(unittest.TestCase):
    def test_all_settings_are_disjoint_and_nonempty(self) -> None:
        frame = make_frame()
        for split in benchmark_splits(frame).values():
            groups = [set(values.tolist()) for values in split.values()]
            self.assertTrue(all(groups))
            self.assertFalse(groups[0] & groups[1])
            self.assertFalse(groups[0] & groups[2])
            self.assertFalse(groups[1] & groups[2])

    def test_same_build_control_contains_only_pivot_build(self) -> None:
        frame = make_frame()
        split = benchmark_splits(frame)[f"same-build-{PIVOT_BUILD}"]
        assigned = set(np.concatenate(list(split.values())).tolist())
        versions = set(frame[frame["row"].isin(assigned)]["version"])
        self.assertEqual(versions, {PIVOT_BUILD})

    def test_unknown_build_fails_instead_of_leaking_into_test(self) -> None:
        frame = make_frame()
        frame.loc[0, "version"] = "9.99.0.0"
        with self.assertRaisesRegex(ValueError, "unknown build"):
            temporal_holdout_split(frame)


if __name__ == "__main__":
    unittest.main()
