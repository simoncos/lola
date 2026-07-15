"""Dataset statistics for the data card (docs/r1-dataset-paper/DATACARD_TEMPLATE.md).

Fills the TODO items of the data card: patch x tier match counts, duration
histogram, champion pick/ban/win table, kill-event timing profile.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def _build_majority_tier_table(cur: sqlite3.Cursor) -> None:
    """Majority previous-season tier per match, as an indexed temp table.

    Single pass + window function; a correlated-subquery version of this
    (evaluated per match, joined through CAST) took hours on the real DB.
    Match.match_id and Participant.match_id are both TEXT, so the final join
    needs no CAST and stays index-backed.
    """
    cur.execute(
        """
        CREATE TEMP TABLE _majority_tier AS
        SELECT match_id, tier FROM (
            SELECT match_id, previous_season_tier AS tier,
                   ROW_NUMBER() OVER (
                       PARTITION BY match_id
                       ORDER BY COUNT(*) DESC, previous_season_tier
                   ) AS rn
            FROM Participant
            GROUP BY match_id, previous_season_tier
        ) WHERE rn = 1
        """
    )
    cur.execute("CREATE INDEX _majority_tier_idx ON _majority_tier(match_id)")


def stats(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    out: dict = {"db": str(db_path)}

    # Patch x majority-tier match counts
    _build_majority_tier_table(cur)
    out["matches_by_version_and_tier"] = [
        {"version": v, "tier": t, "matches": c}
        for v, t, c in cur.execute(
            """
            SELECT m.version, mt.tier, COUNT(*)
            FROM Match m JOIN _majority_tier mt ON mt.match_id = m.match_id
            GROUP BY m.version, mt.tier
            ORDER BY m.version, COUNT(*) DESC
            """
        )
    ]

    # Duration histogram (5-minute buckets; duration column is in minutes)
    out["duration_histogram_5min"] = {
        f"{b * 5}-{b * 5 + 5}min": c
        for b, c in cur.execute(
            "SELECT duration / 5, COUNT(*) FROM Match GROUP BY duration / 5 ORDER BY 1"
        )
    }

    # Champion pick / ban / win table
    out["champions"] = [
        {"champion": ch, "picks": p, "wins": w, "win_rate": round(w / p, 4) if p else None}
        for ch, p, w in cur.execute(
            """
            SELECT champion, COUNT(*), SUM(participant_win)
            FROM Participant GROUP BY champion ORDER BY COUNT(*) DESC
            """
        )
    ]
    bans = dict(cur.execute("SELECT ban, COUNT(*) FROM TeamBan GROUP BY ban"))
    for row in out["champions"]:
        row["bans"] = bans.get(row["champion"], 0)

    # Kill-event timing profile (per 5 minutes, deduplicated)
    out["kills_by_5min"] = {
        f"{b * 5}-{b * 5 + 5}min": c
        for b, c in cur.execute(
            """
            SELECT minute / 5, COUNT(*) FROM (
                SELECT DISTINCT match_id, happen, victim, minute FROM FrameKillEvent
            ) GROUP BY minute / 5 ORDER BY 1
            """
        )
    }

    # Blue-side win rate (side balance check)
    blue = cur.execute(
        "SELECT COUNT(*), SUM(win) FROM Team WHERE side = 'blue'"
    ).fetchone()
    if blue and blue[0]:
        out["blue_side_win_rate"] = round(blue[1] / blue[0], 4)

    conn.close()
    return out


def main(db: str, out: str | None) -> None:
    report = stats(db)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text)
        print(f"stats report written to {out}")
    else:
        print(text)
