from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from lola_dataset.export import EXPORTS, HASH_HEX_CHARS, _anon
from lola_dataset.validate import validate
from tests.make_synthetic_db import main as make_synthetic_db


class ToolkitContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "synthetic.db"
        make_synthetic_db(str(self.db))

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_validator_distinguishes_events_assists_and_exact_duplicates(self) -> None:
        report = validate(str(self.db))
        events = report["kill_events"]
        self.assertTrue(report["quality_gates"]["ok"])
        self.assertEqual(events["distinct_event_keys"], 321)
        self.assertEqual(events["distinct_assist_links"], 40)
        self.assertEqual(events["surplus_rows_over_event_keys"], 21)
        self.assertEqual(events["exact_duplicate_rows"], 1)
        self.assertEqual(events["payload_conflict_event_keys"], 0)

    def test_normalized_event_queries_preserve_all_distinct_assists(self) -> None:
        conn = sqlite3.connect(self.db)
        events = conn.execute(EXPORTS["kill_events"].sql).fetchall()
        assists = conn.execute(EXPORTS["kill_assists"].sql).fetchall()
        conn.close()
        self.assertEqual(len(events), 321)
        self.assertEqual(len(assists), 40)
        self.assertEqual(len({tuple(row[:3]) for row in assists}), 20)

    def test_validator_catches_new_orphan_relations(self) -> None:
        conn = sqlite3.connect(self.db)
        conn.execute("INSERT INTO TeamBan VALUES ('missing', 'blue', 'Ahri')")
        conn.execute(
            "INSERT INTO ParticipantTimeline VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "missing-player",
                "1001",
                "zero_to_ten",
                "blue",
                "99",
                "SOLO",
                "MID",
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ),
        )
        conn.commit()
        conn.close()

        report = validate(str(self.db))
        self.assertFalse(report["quality_gates"]["ok"])
        self.assertEqual(report["referential_integrity"]["TeamBan_match_orphans"], 1)
        self.assertEqual(
            report["referential_integrity"]["ParticipantTimeline_participant_orphans"],
            1,
        )

    def test_validator_rejects_conflicting_event_payload(self) -> None:
        conn = sqlite3.connect(self.db)
        row = conn.execute(
            "SELECT match_id, happen, victim, minute, killer FROM FrameKillEvent LIMIT 1"
        ).fetchone()
        other_killer = conn.execute(
            "SELECT champion FROM Participant WHERE match_id = ? AND champion != ? LIMIT 1",
            (row[0], row[4]),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO FrameKillEvent VALUES (?,?,?,?,?,NULL)",
            (row[0], row[1], row[2], row[3], other_killer),
        )
        conn.commit()
        conn.close()

        report = validate(str(self.db))
        self.assertEqual(report["kill_events"]["payload_conflict_event_keys"], 1)
        self.assertFalse(report["quality_gates"]["ok"])

    def test_missing_database_is_not_created(self) -> None:
        missing = Path(self.tempdir.name) / "missing.db"
        with self.assertRaises(FileNotFoundError):
            validate(str(missing))
        self.assertFalse(missing.exists())

    def test_optional_legacy_table_does_not_block_publication_export(self) -> None:
        conn = sqlite3.connect(self.db)
        conn.execute("DROP TABLE ChampionKillMatrix")
        conn.commit()
        conn.close()
        report = validate(str(self.db))
        self.assertTrue(report["quality_gates"]["ok"])
        self.assertIn(
            "ChampionKillMatrix", report["missing_optional_legacy_tables"]
        )

    def test_missing_required_table_blocks_publication_export(self) -> None:
        conn = sqlite3.connect(self.db)
        conn.execute("DROP TABLE TeamBan")
        conn.commit()
        conn.close()
        report = validate(str(self.db))
        self.assertFalse(report["quality_gates"]["ok"])
        self.assertIn("TeamBan", report["missing_required_tables"])

    def test_pseudonymous_ids_are_stable_and_128_bit(self) -> None:
        value = _anon("player-1", "0123456789abcdef")
        self.assertEqual(value, _anon("player-1", "0123456789abcdef"))
        self.assertEqual(len(value), HASH_HEX_CHARS)
        self.assertNotEqual(value, _anon("player-1", "fedcba9876543210"))


if __name__ == "__main__":
    unittest.main()
