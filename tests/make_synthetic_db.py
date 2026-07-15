"""Build a tiny synthetic lola.db (schema-identical) for smoke-testing the toolkit.

Usage: python tests/make_synthetic_db.py /path/to/test.db
Creates a handful of matches with participants, teams, bans, timelines and
kill events — including one deliberate duplicate kill event and one remake —
so validate/stats/export all exercise their edge-case branches.
"""

import random
import sqlite3
import sys
from pathlib import Path

CHAMPIONS = ["Aatrox", "Ahri", "Akali", "Alistar", "Amumu", "Anivia", "Annie",
             "Ashe", "Azir", "Bard", "Blitzcrank", "Brand", "Braum", "Caitlyn"]
TIERS = ["BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND"]
VERSIONS = ["5.21", "5.22", "5.23", "5.24", "6.1"]

N_MATCHES = 20
random.seed(42)


def main(db_path: str) -> None:
    schema = (Path(__file__).parent.parent / "sqlite_schema.sql").read_text()
    Path(db_path).unlink(missing_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    cur = conn.cursor()

    summoners = [f"summ_{i}" for i in range(60)]
    for s in summoners:
        cur.execute("INSERT INTO Summoner VALUES (?,?,1)", (s, f"Player {s}"))

    for i in range(N_MATCHES):
        match_id = str(1000 + i)
        version = VERSIONS[i % len(VERSIONS)]
        duration = 4 if i == 0 else random.randint(20, 55)  # minutes; match 0 = very short
        cur.execute("INSERT INTO Match VALUES (?,?,?,?,1,1)",
                    (match_id, version, duration, '{"raw": "json-with-names"}'))

        champs = random.sample(CHAMPIONS, 10)
        players = random.sample(summoners, 10)
        cur.execute("INSERT INTO MatchChampion VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (match_id, *champs))
        blue_win = random.randint(0, 1)
        cur.execute("INSERT INTO Team VALUES (?,?,?,?,?)",
                    (match_id, "blue", random.randint(0, 4), random.randint(0, 2), blue_win))
        cur.execute("INSERT INTO Team VALUES (?,?,?,?,?)",
                    (match_id, "red", random.randint(0, 4), random.randint(0, 2), 1 - blue_win))
        for side in ("blue", "red"):
            for ban in random.sample(CHAMPIONS, 3):
                cur.execute("INSERT INTO TeamBan VALUES (?,?,?)", (match_id, side, ban))

        participant_cols = [r[1] for r in cur.execute("PRAGMA table_info(Participant)")]
        for p in range(10):
            side = "blue" if p < 5 else "red"
            win = blue_win if p < 5 else 1 - blue_win
            k, d, a = random.randint(0, 15), random.randint(0, 12), random.randint(0, 20)
            fixed = {
                "summoner_id": players[p], "match_id": match_id,
                "participant_id": str(p + 1), "side": side, "champion": champs[p],
                "previous_season_tier": random.choice(TIERS),
                "summoner_spell_d": "Flash", "summoner_spell_f": "Ignite",
                "kda": round((k + a) / max(d, 1), 2), "kills": k, "deaths": d,
                "assists": a, "participant_win": win,
            }
            values = [fixed.get(c, random.randint(0, 30000)) for c in participant_cols]
            cur.execute(
                "INSERT INTO Participant VALUES ("
                + ",".join(["?"] * len(participant_cols)) + ")",
                values)
            timeline_cols = [r[1] for r in cur.execute("PRAGMA table_info(ParticipantTimeline)")]
            for delta in ("0-10", "10-20", "20-30"):
                tl_fixed = {
                    "summoner_id": players[p], "match_id": match_id, "delta": delta,
                    "side": side, "participant_id": str(p + 1),
                    "role": "SOLO", "lane": "MID",
                }
                tl_values = [tl_fixed.get(c, round(random.uniform(-200, 600), 2))
                             for c in timeline_cols]
                cur.execute(
                    "INSERT INTO ParticipantTimeline VALUES ("
                    + ",".join(["?"] * len(timeline_cols)) + ")",
                    tl_values)

        n_kills = random.randint(5, 25)
        for _ in range(n_kills):
            killer_idx = random.randrange(10)
            victim_pool = range(5, 10) if killer_idx < 5 else range(0, 5)
            victim_idx = random.choice(list(victim_pool))
            happen = random.randint(90, duration * 60)  # seconds within the match
            cur.execute("INSERT INTO FrameKillEvent VALUES (?,?,?,?,?,?)",
                        (match_id, happen, champs[victim_idx], happen // 60,
                         champs[killer_idx], None))
            if i == 1:  # deliberate duplicate rows in match 1
                cur.execute("INSERT INTO FrameKillEvent VALUES (?,?,?,?,?,?)",
                            (match_id, happen, champs[victim_idx], happen // 60,
                             champs[killer_idx], None))

    for c in CHAMPIONS:
        cur.execute(
            "INSERT INTO ChampionMatchStats (champion, picks) VALUES (?, ?)",
            (c, random.randint(1, 20)))

    conn.commit()
    conn.close()
    print(f"synthetic db written to {db_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "test_lola.db")
