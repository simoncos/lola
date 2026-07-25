import unittest

import pandas as pd

from analysis.mastery_learning import (
    MIN_PLAYER_CHAMPION_CELLS,
    cell_sufficient_statistics,
    estimate_champion_learning,
)


class MasteryLearningTests(unittest.TestCase):
    def test_within_cell_learning_recovers_positive_direction(self):
        rows = []
        for player in range(MIN_PLAYER_CHAMPION_CELLS):
            for game in range(1, 6):
                rows.append(
                    {
                        "summoner_id": f"p{player}",
                        "champion": "LearningChampion",
                        "log_experience": float(game - 1),
                        "lane_z": 0.2 * (game - 1) + (player % 3) * 10,
                    }
                )
        cells = cell_sufficient_statistics(pd.DataFrame(rows))
        result = estimate_champion_learning(cells, bootstrap_reps=200, seed=1)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result.iloc[0]["learning_slope"], 0.2, places=7)
        self.assertGreater(result.iloc[0]["ci95_low"], 0)


if __name__ == "__main__":
    unittest.main()
