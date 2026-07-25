import unittest

import pandas as pd

from analysis.design_p2 import match_tier_bucket
from analysis.design_p2_5 import amplification


class DesignContractTests(unittest.TestCase):
    def test_tier_bucket_rejects_ties_and_unranked_heavy_matches(self):
        rows = []
        rows += [
            {"match_id": "clear", "previous_season_tier": tier}
            for tier in ["GOLD"] * 6 + ["SILVER"] * 2 + ["DIAMOND"] * 2
        ]
        rows += [
            {"match_id": "tie", "previous_season_tier": tier}
            for tier in ["GOLD"] * 5 + ["DIAMOND"] * 5
        ]
        rows += [
            {"match_id": "unranked", "previous_season_tier": tier}
            for tier in ["GOLD"] * 5 + ["UNRANKED"] * 5
        ]
        result = match_tier_bucket(pd.DataFrame(rows)).set_index("match_id")
        self.assertEqual(result.loc["clear", "match_bucket"], "mid")
        self.assertNotIn("tie", result.index)
        self.assertNotIn("unranked", result.index)

    def test_transfer_baseline_is_computed_within_position(self):
        rows = []
        for player in range(30):
            for position, offset in [("top", 0.0), ("mid", 100.0)]:
                for champion, value in [("A", 1.0), ("B", 0.0)]:
                    for _ in range(8):
                        rows.append(
                            {
                                "summoner_id": f"p{player}",
                                "position": position,
                                "champion": champion,
                                "lane_z": value + offset + player * 0.01,
                            }
                        )
        result = amplification(pd.DataFrame(rows), "lane_z")
        self.assertEqual(set(result["position"]), {"top", "mid"})
        self.assertEqual(len(result), 4)


if __name__ == "__main__":
    unittest.main()
