"""Export lola.db to anonymized Parquet for publication.

Anonymization (applied during export, source DB is never modified):
- summoner_id  -> salted SHA-256, truncated to 16 hex chars (column kept)
- summoner_name -> dropped entirely
- Match.data (raw API JSON blob, contains player names) -> dropped
- FrameKillEvent deduplicated on (match_id, happen, victim)

The salt must be kept private; without it the hash cannot be linked back to
Riot summoner IDs (which are themselves pre-PUUID and no longer resolvable).
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pandas as pd

CHUNK_ROWS = 500_000

# table -> (SELECT statement, columns to anonymize)
EXPORTS: dict[str, tuple[str, list[str]]] = {
    "matches": (
        "SELECT match_id, version, duration FROM Match",
        [],
    ),
    "teams": (
        "SELECT match_id, side, dragon_kills, baron_kills, win FROM Team",
        [],
    ),
    "team_bans": (
        "SELECT match_id, side, ban FROM TeamBan",
        [],
    ),
    "participants": (
        "SELECT * FROM Participant",
        ["summoner_id"],
    ),
    "participant_timelines": (
        "SELECT * FROM ParticipantTimeline",
        ["summoner_id"],
    ),
    "kill_events": (
        """
        SELECT match_id, happen, victim, minute, killer, assist
        FROM FrameKillEvent
        GROUP BY match_id, happen, victim
        """,
        [],
    ),
    "summoners": (
        "SELECT summoner_id FROM Summoner",
        ["summoner_id"],
    ),
}


def _anon(value: str | None, salt: str) -> str | None:
    if value is None:
        return None
    return hashlib.sha256((salt + str(value)).encode("utf-8")).hexdigest()[:16]


def export(db_path: str, out_dir: str, salt: str, with_version: bool = True) -> None:
    if not salt or len(salt) < 8:
        raise SystemExit("--salt must be at least 8 characters; keep it private")

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)

    version_map = None
    if with_version:
        version_map = pd.read_sql("SELECT match_id, version FROM Match", conn)
        version_map["match_id"] = version_map["match_id"].astype(str)

    for name, (sql, anon_cols) in EXPORTS.items():
        parts = []
        for chunk in pd.read_sql(sql, conn, chunksize=CHUNK_ROWS):
            for col in anon_cols:
                chunk[col] = chunk[col].map(lambda v: _anon(v, salt))
            if (
                version_map is not None
                and "match_id" in chunk.columns
                and "version" not in chunk.columns
            ):
                chunk["match_id"] = chunk["match_id"].astype(str)
                chunk = chunk.merge(version_map, on="match_id", how="left")
            parts.append(chunk)
        if not parts:
            print(f"  {name}: empty, skipped")
            continue
        df = pd.concat(parts, ignore_index=True)
        target = out / f"{name}.parquet"
        df.to_parquet(target, index=False)
        print(f"  {name}: {len(df):,} rows -> {target}")

    conn.close()
    print("done. Reminder: never publish the salt or the original lola.db.")


def main(db: str, out: str, salt: str) -> None:
    export(db, out, salt)
