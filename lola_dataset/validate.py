"""Integrity checks for the legacy lola.db archive.

Produces a JSON report answering the questions that gate cleaning decisions
(see docs/r1-dataset-paper/PLAN.md, milestone M1/M2):

- row counts per table
- duplicate kill events under the (match_id, happen, victim) key
  (the legacy crawler deduplicated by database row order, which is unsafe)
- referential integrity: participants/teams/kill events without a Match row
- per-match cardinality: matches without exactly 10 participants / 2 teams
- very-short-match share (duration < SHORT_MATCH_MINUTES; duration is stored
  in minutes — verified on the real DB, and the era predates remakes)
- matches-per-summoner distribution (feasibility of player-sequence studies)
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from . import SHORT_MATCH_MINUTES, TABLES


def _one(cur: sqlite3.Cursor, sql: str, params: tuple = ()) -> int | float | None:
    return cur.execute(sql, params).fetchone()[0]


def _quantiles(sorted_values: list, points=(0.5, 0.9, 0.99)) -> dict:
    if not sorted_values:
        return {}
    n = len(sorted_values)
    return {f"p{int(p * 100)}": sorted_values[min(n - 1, int(p * n))] for p in points}


def validate(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    report: dict = {"db": str(db_path)}

    existing = {
        r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    report["missing_tables"] = [t for t in TABLES if t not in existing]
    report["row_counts"] = {
        t: _one(cur, f"SELECT COUNT(*) FROM {t}") for t in TABLES if t in existing
    }

    n_matches = report["row_counts"].get("Match", 0)

    # --- Match-level sanity -------------------------------------------------
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

    # --- Kill-event duplicates ----------------------------------------------
    if "FrameKillEvent" in existing:
        dup_rows = _one(
            cur,
            """
            SELECT COALESCE(SUM(c - 1), 0) FROM (
                SELECT COUNT(*) AS c FROM FrameKillEvent
                GROUP BY match_id, happen, victim HAVING c > 1
            )
            """,
        )
        total = report["row_counts"]["FrameKillEvent"]
        report["kill_events"] = {
            "total_rows": total,
            "surplus_duplicate_rows": dup_rows,
            "duplicate_share": round(dup_rows / total, 6) if total else 0.0,
        }

    # --- Referential integrity ----------------------------------------------
    # Match IDs are stored inconsistently (TEXT in Match, INTEGER in
    # MatchChampion); normalize once into an indexed temp table so the orphan
    # checks stay index-backed even on the 21.7M-row kill-event table.
    integrity = {}
    if "Match" in existing:
        cur.execute(
            "CREATE TEMP TABLE _mid AS SELECT CAST(match_id AS TEXT) AS mid FROM Match"
        )
        cur.execute("CREATE INDEX _mid_idx ON _mid(mid)")
        for table, fk in [
            ("Participant", "match_id"),
            ("Team", "match_id"),
            ("FrameKillEvent", "match_id"),
            ("MatchChampion", "match_id"),
        ]:
            if table in existing:
                integrity[f"{table}_orphans"] = _one(
                    cur,
                    f"""
                    SELECT COUNT(*) FROM {table} t
                    WHERE CAST(t.{fk} AS TEXT) NOT IN (SELECT mid FROM _mid)
                    """,
                )
    report["referential_integrity"] = integrity

    # --- Per-match cardinality ----------------------------------------------
    cardinality = {}
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
        cardinality["matches_missing_participants"] = n_matches - _one(
            cur, "SELECT COUNT(DISTINCT match_id) FROM Participant"
        )
    if {"Team", "Match"} <= existing:
        cardinality["matches_without_2_teams"] = _one(
            cur,
            "SELECT COUNT(*) FROM (SELECT match_id FROM Team GROUP BY match_id HAVING COUNT(*) != 2)",
        )
    if {"Team"} <= existing:
        cardinality["matches_without_single_winner"] = _one(
            cur,
            "SELECT COUNT(*) FROM (SELECT match_id FROM Team GROUP BY match_id HAVING SUM(win) != 1)",
        )
    report["cardinality"] = cardinality

    # --- Matches per summoner (player-sequence feasibility) -------------------
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

    # --- Tier coverage --------------------------------------------------------
    if "Participant" in existing:
        report["previous_season_tiers"] = dict(
            cur.execute(
                """
                SELECT COALESCE(previous_season_tier, 'NULL'), COUNT(*)
                FROM Participant GROUP BY previous_season_tier
                """
            ).fetchall()
        )

    conn.close()
    return report


def main(db: str, out: str | None) -> None:
    report = validate(db)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text)
        print(f"validate report written to {out}")
    else:
        print(text)
