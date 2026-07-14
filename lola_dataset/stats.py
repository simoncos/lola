"""Dataset statistics for the data card (docs/r1-dataset-paper/DATACARD_TEMPLATE.md).

Fills the TODO items of the data card: patch x tier match counts, duration
histogram, champion pick/ban/win table, kill-event timing profile.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def _match_tier_expr() -> str:
    """Majority previous-season tier of the 10 participants of a match."""
    return """
        SELECT p.match_id AS match_id,
               (SELECT previous_season_tier FROM Participant q
                WHERE q.match_id = p.match_id
                GROUP BY previous_season_tier
                ORDER BY COUNT(*) DESC LIMIT 1) AS avg_tier
        FROM Participant p GROUP BY p.match_id
    """


def stats(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    out: dict = {"db": str(db_path)}

    # Patch x majority-tier match counts
    out["matches_by_version_and_tier"] = [
        {"version": v, "tier": t, "matches": c}
        for v, t, c in cur.execute(
            f"""
            SELECT m.version, mt.avg_tier, COUNT(*)
            FROM Match m JOIN ({_match_tier_expr()}) mt
              ON CAST(mt.match_id AS TEXT) = CAST(m.match_id AS TEXT)
            GROUP BY m.version, mt.avg_tier
            ORDER BY m.version, COUNT(*) DESC
            """
        )
    ]

    # Duration histogram (5-minute buckets)
    out["duration_histogram_5min"] = {
        f"{b * 5}-{b * 5 + 5}min": c
        for b, c in cur.execute(
            "SELECT duration / 300, COUNT(*) FROM Match GROUP BY duration / 300 ORDER BY 1"
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
