import tempfile
import unittest
from pathlib import Path

from lola_dataset.stats import stats
from tests.make_synthetic_db import main as make_synthetic_db


class StatsContractTests(unittest.TestCase):
    def test_stats_uses_ranked_bucket_and_normalized_events(self):
        with tempfile.TemporaryDirectory() as tempdir:
            database = Path(tempdir) / "synthetic.db"
            make_synthetic_db(str(database))
            report = stats(str(database))
            self.assertIn("matches_by_version_and_tier_bucket", report)
            self.assertEqual(sum(report["kills_by_5min"].values()), 321)

    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as tempdir:
            database = Path(tempdir) / "missing.db"
            with self.assertRaises(FileNotFoundError):
                stats(str(database))
            self.assertFalse(database.exists())


if __name__ == "__main__":
    unittest.main()
