from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from lola_dataset.export import export
from tests.make_synthetic_db import main as make_synthetic_db


@unittest.skipUnless(importlib.util.find_spec("pyarrow"), "pyarrow is not installed")
class ExportIntegrationTests(unittest.TestCase):
    def test_atomic_export_preserves_event_and_assist_relations(self) -> None:
        import pandas as pd

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            db = root / "synthetic.db"
            out = root / "parquet"
            make_synthetic_db(str(db))

            export(str(db), str(out), "0123456789abcdef")

            events = pd.read_parquet(out / "kill_events.parquet")
            assists = pd.read_parquet(out / "kill_assists.parquet")
            participants = pd.read_parquet(out / "participants.parquet")
            manifest = json.loads((out / "manifest.json").read_text())
            audit = json.loads((out / "validation.json").read_text())

            self.assertEqual(len(events), 321)
            self.assertEqual(len(assists), 40)
            self.assertNotIn("assist", events.columns)
            self.assertEqual(participants["summoner_id"].str.len().unique().tolist(), [32])
            self.assertEqual(manifest["format_version"], 2)
            self.assertIn("git_dirty", manifest)
            self.assertEqual(manifest["source_tree"]["algorithm"], "SHA-256(path + file SHA-256)")
            self.assertGreater(manifest["source_tree"]["files"], 0)
            self.assertEqual(manifest["outputs"]["kill_events"]["rows"], 321)
            self.assertEqual(manifest["outputs"]["kill_assists"]["rows"], 40)
            self.assertFalse(manifest["pseudonymization"]["salt_included"])
            self.assertEqual(
                manifest["pseudonymization"]["algorithm"], "HMAC-SHA-256"
            )
            self.assertTrue(audit["quality_gates"]["ok"])
            self.assertEqual(
                manifest["validation_report"]["file"], "validation.json"
            )


if __name__ == "__main__":
    unittest.main()
