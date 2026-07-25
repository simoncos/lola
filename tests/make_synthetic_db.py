"""Build a tiny synthetic lola.db (schema-identical) for smoke-testing the toolkit.

Usage: python tests/make_synthetic_db.py /path/to/test.db
Creates a handful of matches with participants, teams, bans, production-shaped
timelines and kill events.  The event fixture includes both legitimate
one-row-per-assist expansion and one exact duplicate assist row so the
validator can distinguish the two cases.
"""

import random
import sqlite3
import sys
from pathlib import Path

CHAMPIONS = ["Aatrox", "Ahri", "Akali", "Alistar", "Amumu", "Anivia", "Annie",
             "Ashe", "Azir", "Bard", "Blitzcrank", "Brand", "Braum", "Caitlyn"]
TIERS = ["BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND"]
VERSIONS = [
    "5.21.0.297",
    "5.22.0.297",
    "5.23.0.239",
    "5.24.0.256",
    "6.1.0.484",
]
TIMELINE_SEGMENTS = [
    "zero_to_ten",
    "ten_to_twenty",
    "twenty_to_thirty",
    "thirty_to_end",
]
POSITIONS = [
    ("TOP", "SOLO"),
    ("JUNGLE", "NONE"),
    ("MIDDLE", "SOLO"),
    ("BOTTOM", "DUO_CARRY"),
    ("BOTTOM", "DUO_SUPPORT"),
]

N_MATCHES = 20


def main(db_path: str) -> None:
    rng = random.Random(42)
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
        duration = 4 if i == 0 else rng.randint(20, 55)  # minutes; match 0 = very short
        cur.execute("INSERT INTO Match VALUES (?,?,?,?,1,1)",
                    (match_id, version, duration, '{"raw": "json-with-names"}'))

        champs = rng.sample(CHAMPIONS, 10)
        players = rng.sample(summoners, 10)
        cur.execute("INSERT INTO MatchChampion VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (match_id, *champs))
        blue_win = rng.randint(0, 1)
        cur.execute("INSERT INTO Team VALUES (?,?,?,?,?)",
                    (match_id, "blue", rng.randint(0, 4), rng.randint(0, 2), blue_win))
        cur.execute("INSERT INTO Team VALUES (?,?,?,?,?)",
                    (match_id, "red", rng.randint(0, 4), rng.randint(0, 2), 1 - blue_win))
        for side in ("blue", "red"):
            for ban in rng.sample(CHAMPIONS, 3):
                cur.execute("INSERT INTO TeamBan VALUES (?,?,?)", (match_id, side, ban))

        participant_cols = [r[1] for r in cur.execute("PRAGMA table_info(Participant)")]
        for p in range(10):
            side = "blue" if p < 5 else "red"
            win = blue_win if p < 5 else 1 - blue_win
            k, d, a = rng.randint(0, 15), rng.randint(0, 12), rng.randint(0, 20)
            fixed = {
                "summoner_id": players[p], "match_id": match_id,
                "participant_id": str(p + 1), "side": side, "champion": champs[p],
                "previous_season_tier": rng.choice(TIERS),
                "summoner_spell_d": "Flash", "summoner_spell_f": "Ignite",
                "kda": round((k + a) / max(d, 1), 2), "kills": k, "deaths": d,
                "assists": a, "participant_win": win,
            }
            values = [fixed.get(c, rng.randint(0, 30000)) for c in participant_cols]
            cur.execute(
                "INSERT INTO Participant VALUES ("
                + ",".join(["?"] * len(participant_cols)) + ")",
                values)
            timeline_cols = [r[1] for r in cur.execute("PRAGMA table_info(ParticipantTimeline)")]
            lane, role = POSITIONS[p % 5]
            for delta in TIMELINE_SEGMENTS:
                tl_fixed = {
                    "summoner_id": players[p], "match_id": match_id, "delta": delta,
                    "side": side, "participant_id": str(p + 1),
                    "role": role, "lane": lane,
                }
                tl_values = [tl_fixed.get(c, round(rng.uniform(-200, 600), 2))
                             for c in timeline_cols]
                cur.execute(
                    "INSERT INTO ParticipantTimeline VALUES ("
                    + ",".join(["?"] * len(timeline_cols)) + ")",
                    tl_values)

        n_kills = rng.randint(5, 25)
        for event_index in range(n_kills):
            killer_idx = rng.randrange(10)
            victim_pool = range(5, 10) if killer_idx < 5 else range(0, 5)
            victim_idx = rng.choice(list(victim_pool))
            happen = min(90 + event_index * 5, duration * 60 - 1)
            ally_pool = list(range(0, 5) if killer_idx < 5 else range(5, 10))
            ally_pool.remove(killer_idx)
            assists = rng.sample(ally_pool, k=2) if event_index == 0 else []
            if assists:
                for assist_idx in assists:
                    cur.execute(
                        "INSERT INTO FrameKillEvent VALUES (?,?,?,?,?,?)",
                        (
                            match_id,
                            happen,
                            champs[victim_idx],
                            happen // 60,
                            champs[killer_idx],
                            champs[assist_idx],
                        ),
                    )
            else:
                cur.execute("INSERT INTO FrameKillEvent VALUES (?,?,?,?,?,?)",
                            (match_id, happen, champs[victim_idx], happen // 60,
                             champs[killer_idx], None))
            if i == 1 and event_index == 0:
                # One exact duplicate of an assist link, distinct from the
                # legitimate second assist row for the same kill event.
                cur.execute(
                    "INSERT INTO FrameKillEvent VALUES (?,?,?,?,?,?)",
                    (
                        match_id,
                        happen,
                        champs[victim_idx],
                        happen // 60,
                        champs[killer_idx],
                        champs[assists[0]],
                    ),
                )

    for c in CHAMPIONS:
        cur.execute(
            "INSERT INTO ChampionMatchStats (champion, picks) VALUES (?, ?)",
            (c, rng.randint(1, 20)))

    conn.commit()
    conn.close()
    print(f"synthetic db written to {db_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "test_lola.db")
