"""Integrity checks for the legacy ``lola.db`` archive.

The original crawler stores one ``FrameKillEvent`` row per assist.  Rows that
share ``(match_id, happen, victim)`` therefore represent one kill event with
zero or more assist links; they are not automatically duplicate events.  This
validator keeps those concepts separate and supplies publication gates for the
relational and event-level invariants used by the Parquet exporter.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from . import OPTIONAL_LEGACY_TABLES, REQUIRED_TABLES, SHORT_MATCH_MINUTES, TABLES


EXPECTED_TIMELINE_SEGMENTS = 4
EXPECTED_TIMELINE_DELTAS = {
    "zero_to_ten",
    "ten_to_twenty",
    "twenty_to_thirty",
    "thirty_to_end",
}


def _one(cur: sqlite3.Cursor, sql: str, params: tuple = ()) -> int | float | None:
    return cur.execute(sql, params).fetchone()[0]


def _quantiles(sorted_values: list, points=(0.5, 0.9, 0.99)) -> dict:
    if not sorted_values:
        return {}
    n = len(sorted_values)
    return {f"p{int(p * 100)}": sorted_values[min(n - 1, int(p * n))] for p in points}


def _connect_read_only(db_path: str) -> sqlite3.Connection:
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"database does not exist: {path}")
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _build_key_tables(cur: sqlite3.Cursor, existing: set[str]) -> None:
    if "Match" in existing:
        cur.execute(
            "CREATE TEMP TABLE _mid AS SELECT CAST(match_id AS TEXT) AS mid FROM Match"
        )
        cur.execute("CREATE INDEX _mid_idx ON _mid(mid)")
        cur.execute(
            """
            CREATE TEMP TABLE _match_duration AS
            SELECT CAST(match_id AS TEXT) AS mid, duration FROM Match
            """
        )
        cur.execute("CREATE INDEX _match_duration_idx ON _match_duration(mid)")
    if "Summoner" in existing:
        cur.execute(
            """
            CREATE TEMP TABLE _summoner_key AS
            SELECT DISTINCT CAST(summoner_id AS TEXT) AS sid FROM Summoner
            """
        )
        cur.execute("CREATE INDEX _summoner_key_idx ON _summoner_key(sid)")
    if "Participant" in existing:
        cur.execute(
            """
            CREATE TEMP TABLE _participant_key AS
            SELECT DISTINCT CAST(match_id AS TEXT) AS mid,
                            CAST(summoner_id AS TEXT) AS sid
            FROM Participant
            """
        )
        cur.execute("CREATE INDEX _participant_key_idx ON _participant_key(mid, sid)")
        cur.execute(
            "CREATE TEMP TABLE _participant_match AS SELECT DISTINCT mid FROM _participant_key"
        )
        cur.execute("CREATE INDEX _participant_match_idx ON _participant_match(mid)")
        cur.execute(
            """
            CREATE TEMP TABLE _match_champion AS
            SELECT DISTINCT CAST(match_id AS TEXT) AS mid, champion
            FROM Participant
            """
        )
        cur.execute("CREATE INDEX _match_champion_idx ON _match_champion(mid, champion)")


def _kill_event_audit(cur: sqlite3.Cursor, total: int) -> dict:
    distinct_events = _one(
        cur,
        """
        SELECT COUNT(*) FROM (
            SELECT 1 FROM FrameKillEvent
            GROUP BY match_id, happen, victim
        )
        """,
    )
    event_keys_with_multiple_rows = _one(
        cur,
        """
        SELECT COUNT(*) FROM (
            SELECT 1 FROM FrameKillEvent
            GROUP BY match_id, happen, victim HAVING COUNT(*) > 1
        )
        """,
    )
    exact_duplicate_rows = _one(
        cur,
        """
        SELECT COALESCE(SUM(c - 1), 0) FROM (
            SELECT COUNT(*) AS c FROM FrameKillEvent
            GROUP BY match_id, happen, victim, minute, killer,
                     COALESCE(assist, '')
            HAVING c > 1
        )
        """,
    )
    payload_conflict_event_keys = _one(
        cur,
        """
        SELECT COUNT(*) FROM (
            SELECT 1 FROM FrameKillEvent
            GROUP BY match_id, happen, victim
            HAVING COUNT(DISTINCT minute) > 1
                OR (COUNT(minute) > 0 AND COUNT(minute) < COUNT(*))
                OR COUNT(DISTINCT killer) > 1
                OR (COUNT(killer) > 0 AND COUNT(killer) < COUNT(*))
        )
        """,
    )
    distinct_assist_links = _one(
        cur,
        """
        SELECT COUNT(*) FROM (
            SELECT 1 FROM FrameKillEvent WHERE assist IS NOT NULL
            GROUP BY match_id, happen, victim, assist
        )
        """,
    )
    return {
        "raw_rows": total,
        "distinct_event_keys": distinct_events,
        "event_keys_with_multiple_rows": event_keys_with_multiple_rows,
        "surplus_rows_over_event_keys": total - distinct_events,
        "distinct_assist_links": distinct_assist_links,
        "exact_duplicate_rows": exact_duplicate_rows,
        "payload_conflict_event_keys": payload_conflict_event_keys,
        "note": (
            "Multiple rows per event key can encode different assists. Only exact "
            "six-field duplicates are duplicate rows."
        ),
    }


def _quality_gate_errors(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("missing_required_tables"):
        errors.append("required tables are missing")
    for name, value in report.get("referential_integrity", {}).items():
        if value:
            errors.append(f"{name}={value}")
    for name, value in report.get("cardinality", {}).items():
        if value:
            errors.append(f"{name}={value}")
    for name, value in report.get("event_integrity", {}).items():
        if value:
            errors.append(f"{name}={value}")
    conflicts = report.get("kill_events", {}).get("payload_conflict_event_keys", 0)
    if conflicts:
        errors.append(f"kill_event_payload_conflicts={conflicts}")
    return errors


def validate(db_path: str) -> dict:
    conn = _connect_read_only(db_path)
    cur = conn.cursor()
    report: dict = {"db": str(Path(db_path).expanduser().resolve())}

    existing = {
        r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    report["missing_required_tables"] = [
        table for table in REQUIRED_TABLES if table not in existing
    ]
    report["missing_optional_legacy_tables"] = [
        table for table in OPTIONAL_LEGACY_TABLES if table not in existing
    ]
    report["row_counts"] = {
        t: _one(cur, f"SELECT COUNT(*) FROM {t}") for t in TABLES if t in existing
    }
    _build_key_tables(cur, existing)

    if "Match" in existing:
        report["match"] = {
            "distinct_match_ids": _one(cur, "SELECT COUNT(DISTINCT match_id) FROM Match"),
            "versions": dict(
                cur.execute(
                    "SELECT version, COUNT(*) FROM Match GROUP BY version ORDER BY version"
                ).fetchall()
            ),
            "duration_min_minutes": _one(cur, "SELECT MIN(duration) FROM Match"),
            "duration_max_minutes": _one(cur, "SELECT MAX(duration) FROM Match"),
            "very_short_lt_%dmin" % SHORT_MATCH_MINUTES: _one(
                cur,
                "SELECT COUNT(*) FROM Match WHERE duration < ?",
                (SHORT_MATCH_MINUTES,),
            ),
        }
        report["cardinality"] = {
            "duplicate_match_ids": _one(
                cur,
                "SELECT COUNT(*) FROM (SELECT match_id FROM Match GROUP BY match_id HAVING COUNT(*) > 1)",
            )
        }

    if "FrameKillEvent" in existing:
        report["kill_events"] = _kill_event_audit(
            cur, report["row_counts"]["FrameKillEvent"]
        )

    integrity: dict[str, int | float | None] = {}
    if "Match" in existing:
        for table, fk in [
            ("Participant", "match_id"),
            ("ParticipantTimeline", "match_id"),
            ("Team", "match_id"),
            ("TeamBan", "match_id"),
            ("FrameKillEvent", "match_id"),
            ("MatchChampion", "match_id"),
        ]:
            if table in existing:
                integrity[f"{table}_match_orphans"] = _one(
                    cur,
                    f"""
                    SELECT COUNT(*) FROM {table} t
                    WHERE CAST(t.{fk} AS TEXT) NOT IN (SELECT mid FROM _mid)
                    """,
                )
    if {"Participant", "Summoner"} <= existing:
        integrity["Participant_summoner_orphans"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM Participant p
            WHERE NOT EXISTS (
                SELECT 1 FROM _summoner_key s
                WHERE s.sid = CAST(p.summoner_id AS TEXT)
            )
            """,
        )
    if {"ParticipantTimeline", "Participant"} <= existing:
        integrity["ParticipantTimeline_participant_orphans"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM ParticipantTimeline t
            WHERE NOT EXISTS (
                SELECT 1 FROM _participant_key p
                WHERE p.mid = CAST(t.match_id AS TEXT)
                  AND p.sid = CAST(t.summoner_id AS TEXT)
            )
            """,
        )
    report["referential_integrity"] = integrity

    cardinality: dict[str, int | float | None] = report.get("cardinality", {})
    if {"Participant", "Match"} <= existing:
        cardinality["matches_without_10_participants"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM (
                SELECT match_id FROM Participant GROUP BY match_id
                HAVING COUNT(*) != 10
            )
            """,
        )
        cardinality["matches_missing_participants"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM _mid m
            WHERE NOT EXISTS (SELECT 1 FROM _participant_match p WHERE p.mid = m.mid)
            """,
        )
        cardinality["matches_without_10_unique_summoners"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM (
                SELECT match_id FROM Participant GROUP BY match_id
                HAVING COUNT(DISTINCT summoner_id) != 10
            )
            """,
        )
    if {"Team", "Match"} <= existing:
        cur.execute(
            "CREATE TEMP TABLE _team_match AS SELECT DISTINCT CAST(match_id AS TEXT) AS mid FROM Team"
        )
        cur.execute("CREATE INDEX _team_match_idx ON _team_match(mid)")
        cardinality["matches_without_2_teams"] = _one(
            cur,
            "SELECT COUNT(*) FROM (SELECT match_id FROM Team GROUP BY match_id HAVING COUNT(*) != 2)",
        )
        cardinality["matches_missing_teams"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM _mid m
            WHERE NOT EXISTS (SELECT 1 FROM _team_match t WHERE t.mid = m.mid)
            """,
        )
        cardinality["matches_without_single_winner"] = _one(
            cur,
            "SELECT COUNT(*) FROM (SELECT match_id FROM Team GROUP BY match_id HAVING SUM(win) != 1)",
        )
        cardinality["matches_without_blue_and_red"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM (
                SELECT match_id FROM Team GROUP BY match_id
                HAVING SUM(CASE WHEN side = 'blue' THEN 1 ELSE 0 END) != 1
                    OR SUM(CASE WHEN side = 'red' THEN 1 ELSE 0 END) != 1
            )
            """,
        )
    if {"ParticipantTimeline", "Participant"} <= existing:
        cur.execute(
            """
            CREATE TEMP TABLE _timeline_counts AS
            SELECT CAST(match_id AS TEXT) AS mid,
                   CAST(summoner_id AS TEXT) AS sid,
                   COUNT(*) AS rows,
                   COUNT(DISTINCT delta) AS segments
            FROM ParticipantTimeline
            GROUP BY match_id, summoner_id
            """
        )
        cur.execute("CREATE INDEX _timeline_counts_idx ON _timeline_counts(mid, sid)")
        cardinality["participants_without_4_unique_timeline_segments"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM _participant_key p
            LEFT JOIN _timeline_counts t ON t.mid = p.mid AND t.sid = p.sid
            WHERE COALESCE(t.rows, 0) != ? OR COALESCE(t.segments, 0) != ?
            """,
            (EXPECTED_TIMELINE_SEGMENTS, EXPECTED_TIMELINE_SEGMENTS),
        )
        placeholders = ", ".join("?" for _ in EXPECTED_TIMELINE_DELTAS)
        cardinality["timeline_rows_with_unknown_delta"] = _one(
            cur,
            f"SELECT COUNT(*) FROM ParticipantTimeline WHERE delta NOT IN ({placeholders})",
            tuple(sorted(EXPECTED_TIMELINE_DELTAS)),
        )
    report["cardinality"] = cardinality

    event_integrity: dict[str, int | float | None] = {}
    if {"FrameKillEvent", "Match"} <= existing:
        event_integrity["kill_rows_after_match_duration"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM FrameKillEvent k
            JOIN _match_duration m ON m.mid = CAST(k.match_id AS TEXT)
            WHERE k.minute > m.duration
            """,
        )
        event_integrity["kill_rows_with_negative_minute"] = _one(
            cur, "SELECT COUNT(*) FROM FrameKillEvent WHERE minute < 0"
        )
    if {"FrameKillEvent", "Participant"} <= existing:
        event_integrity["kill_rows_with_unknown_killer"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM FrameKillEvent k
            WHERE k.killer IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM _match_champion mc
                WHERE mc.mid = CAST(k.match_id AS TEXT) AND mc.champion = k.killer
            )
            """,
        )
        event_integrity["kill_rows_with_unknown_victim"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM FrameKillEvent k
            WHERE NOT EXISTS (
                SELECT 1 FROM _match_champion mc
                WHERE mc.mid = CAST(k.match_id AS TEXT) AND mc.champion = k.victim
            )
            """,
        )
        event_integrity["assist_rows_with_unknown_assist"] = _one(
            cur,
            """
            SELECT COUNT(*) FROM FrameKillEvent k
            WHERE k.assist IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM _match_champion mc
                WHERE mc.mid = CAST(k.match_id AS TEXT) AND mc.champion = k.assist
            )
            """,
        )
    report["event_integrity"] = event_integrity
    if "FrameKillEvent" in existing:
        report["event_diagnostics"] = {
            "kill_rows_without_killer": _one(
                cur, "SELECT COUNT(*) FROM FrameKillEvent WHERE killer IS NULL"
            )
        }

    if "TeamBan" in existing:
        report["team_bans_per_match"] = dict(
            cur.execute(
                """
                SELECT CAST(c AS TEXT), COUNT(*) FROM (
                    SELECT match_id, COUNT(*) AS c FROM TeamBan GROUP BY match_id
                ) GROUP BY c ORDER BY c
                """
            ).fetchall()
        )

    if "Participant" in existing:
        counts = [
            r[0]
            for r in cur.execute(
                "SELECT COUNT(*) FROM Participant GROUP BY summoner_id ORDER BY COUNT(*)"
            )
        ]
        report["matches_per_summoner"] = {
            "summoners": len(counts),
            "mean": round(sum(counts) / len(counts), 2) if counts else 0,
            **_quantiles(counts),
            "with_ge_20_matches": sum(1 for c in counts if c >= 20),
            "with_ge_50_matches": sum(1 for c in counts if c >= 50),
        }
        report["previous_season_tiers"] = dict(
            cur.execute(
                """
                SELECT COALESCE(previous_season_tier, 'NULL'), COUNT(*)
                FROM Participant GROUP BY previous_season_tier
                """
            ).fetchall()
        )

    errors = _quality_gate_errors(report)
    report["quality_gates"] = {"ok": not errors, "errors": errors}
    conn.close()
    return report


def main(db: str, out: str | None, strict: bool = False) -> None:
    report = validate(db)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text)
        print(f"validate report written to {out}")
    else:
        print(text)
    if strict and not report["quality_gates"]["ok"]:
        raise SystemExit(2)
