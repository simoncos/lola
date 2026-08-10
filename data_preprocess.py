from contextlib import closing
import sqlite3
import time

'''
Update MatchChampion:
1. SELECT match_id FROM Match
2. SELECT champion FROM Participant WHERE match_id = ? ORDER BY participant_id
3. INSERT INTO MatchChampion VALUES(match_id, participant1, ...)
'''
def match_champion_to_sqlite(db_path='lola.db'):
    print('Updating participants of matches to MatchChampion...')
    st = time.time()
    with closing(sqlite3.connect(db_path)) as conn, conn:
        cursor = conn.cursor()
        match_ids = cursor.execute(
            'SELECT match_id FROM Match ORDER BY match_id'
        ).fetchall()

        # Rebuild atomically so rerunning preprocessing cannot append duplicates.
        cursor.execute('DELETE FROM MatchChampion')
        for (match_id,) in match_ids:
            participants = cursor.execute(
                'SELECT champion FROM Participant WHERE match_id = ? '
                'ORDER BY CAST(participant_id AS INTEGER)',
                (match_id,),
            ).fetchall()
            if len(participants) != 10:
                raise ValueError(
                    'Match {} has {} participants; expected 10'.format(
                        match_id, len(participants)
                    )
                )

            champion_names = [
                value.decode('utf-8') if isinstance(value, bytes) else value
                for (value,) in participants
            ]
            cursor.execute(
                'INSERT INTO MatchChampion VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                (match_id,) + tuple(champion_names),
            )

    print('Done.\nElapsed time: %.2fs.\n' % (time.time()-st))
    return len(match_ids)

'''
Refresh ChampionMatchStats from Participant and TeamBan:
1. Enumerate champions present in Participant.
2. Recompute every aggregate used by downstream analysis.
3. Update an existing row or insert a new one without resetting labels/metadata.
'''
def champion_match_stats_to_sqlite(db_path='lola.db'):
    print('Updating champion stats of matches to ChampionMatchStats...')
    st = time.time()
    with closing(sqlite3.connect(db_path)) as conn, conn:
        cursor = conn.cursor()
        champion_names = [
            row[0]
            for row in cursor.execute(
                'SELECT DISTINCT champion FROM Participant ORDER BY champion'
            ).fetchall()
        ]

        for champion in champion_names:
            aggregates = cursor.execute(
                '''
                SELECT COUNT(*),
                       COALESCE(SUM(participant_win), 0),
                       COALESCE(SUM(kills), 0),
                       COALESCE(SUM(deaths), 0),
                       COALESCE(SUM(assists), 0),
                       COALESCE(SUM(gold_earned), 0),
                       COALESCE(SUM(magic_damage_dealt_to_champions), 0),
                       COALESCE(SUM(physical_damage_dealt_to_champions), 0),
                       COALESCE(SUM(true_damage_dealt_to_champions), 0),
                       COALESCE(SUM(damage_taken), 0),
                       COALESCE(SUM(crowd_control_dealt), 0),
                       COALESCE(SUM(ward_kills), 0),
                       COALESCE(SUM(wards_placed), 0)
                FROM Participant
                WHERE champion = ?
                ''',
                (champion,),
            ).fetchone()
            bans = cursor.execute(
                'SELECT COUNT(*) FROM TeamBan WHERE ban = ?', (champion,)
            ).fetchone()[0]
            values = (
                aggregates[0], bans, aggregates[1],
                *aggregates[2:],
            )

            cursor.execute(
                '''
                UPDATE ChampionMatchStats
                SET picks = ?, bans = ?, wins = ?, kills = ?, deaths = ?,
                    assists = ?, gold_earned = ?, magic_damage = ?,
                    physical_damage = ?, true_damage = ?, damage_taken = ?,
                    crowd_control_dealt = ?, ward_kills = ?, wards_placed = ?
                WHERE champion = ?
                ''',
                values + (champion,),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    '''
                    INSERT INTO ChampionMatchStats(
                        champion, picks, bans, wins, kills, deaths, assists,
                        gold_earned, magic_damage, physical_damage, true_damage,
                        damage_taken, crowd_control_dealt, ward_kills, wards_placed
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ''',
                    (champion,) + values,
                )

    print('Done.\nElapsed time: %.2fs\n' % (time.time() - st))
    return len(champion_names)

# TODO: ChampionMatchStats and ChampionRank Initialization (insert or update), in case that champion / match data updating from crawling

'''TODO: average tier of match
def select_version_tier():
    conn = sqlite3.connect(addr_db)
    cursor = conn.execute("SELECT match_id,version from Match")
    for row in cursor:
        all_matchid.append(row[0])
        all_version.append(row[1])
        if row[1] not in version:
            version.append(row[1])
    
    cursor = conn.execute("SELECT previous_season_tier from Participant")
    count = 1
    temp_avg_tier = []
    for row in cursor:
        if row[0] not in tier: # collect all tier
            tier.append(row[0])
        if count%10!=0: # collect match tier level
            temp_avg_tier.append(row[0])
            count += 1
        else:
            avg_tier.append(most_common(temp_avg_tier))
            count = 1
            temp_avg_tier = []
    conn.close
    for i in range(len(all_matchid)):
        all_matchid[i] = all_matchid[i].encode("ascII")
        avg_tier[i] = avg_tier[i].encode("ascII")

def insert_avgtier():
    conn = sqlite3.connect(addr_db)
    conn.execute("ALTER TABLE Match ADD COLUMN TIER TEXT") # Add COLUMN in Match(#should be dropped)
    for i in range(len(avg_tier)): # insert the average match tier
        conn.execute("UPDATE Match SET TIER=? WHERE match_id=?",(avg_tier[i],all_matchid[i]))
    conn.commit()
    print '$-----Table:Match Mission:avg_tier update [Finished].-----$' 
    conn.execute("ALTER TABLE FrameKillEvent ADD COLUMN avg_tier TEXT") # Add COLUMN in Frame(#should be dropped)
    conn.execute("ALTER TABLE FrameKillEvent ADD COLUMN version TEXT") # Add COLUMN in Frame(#should be dropped)
    conn.execute("UPDATE FrameKillEvent SET avg_tier = (SELECT TIER FROM Match WHERE Match.match_id = FrameKillEvent.match_id)")
    conn.execute("UPDATE FrameKillEvent SET version = (SELECT version FROM Match WHERE Match.match_id = FrameKillEvent.match_id)")
    print '$-----Table:FrameKillEvent Mission:avg_tier&version update [Finished].-----$'
    conn.commit()
    conn.close()

def most_common(L):
    return max(g(sorted(L)), key=lambda(x, v):(len(list(v)),-L.index(x)))[0]
'''
