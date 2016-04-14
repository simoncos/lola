import sqlite3
import time
from statics import champions

'''
Update MatchChampion:
1. SELECT match_id FROM Match
2. SELECT champion FROM Participant WHERE match_id = ? ORDER BY participant_id
3. INSERT INTO MatchChampion VALUES(match_id, participant1, ...)
'''
def match_champion_to_sqlite():
    conn = sqlite3.connect('lola.db')
    cursor = conn.cursor()

    print('Updating participants of matches to MatchChampion...')

    # Select uncounted match_ids
    cursor.execute('SELECT match_id FROM Match')
    result = cursor.fetchall()

    st = time.time()
    for item in result:
    # Select participants of each match
        match_id = int(item[0].encode('utf-8'))
        cursor.execute('SELECT champion FROM Participant WHERE match_id = ? ORDER BY CAST(participant_id AS INTEGER)', (match_id,))
        participants = cursor.fetchall()
    # Insert participants into MatchChampion
        cursor.execute('INSERT INTO MatchChampion VALUES(?,?,?,?,?,?,?,?,?,?,?)', (match_id, participants[0][0].encode('utf-8'),
            participants[1][0].encode('utf-8'),participants[2][0].encode('utf-8'), participants[3][0].encode('utf-8'),
            participants[4][0].encode('utf-8'),participants[5][0].encode('utf-8'), participants[6][0].encode('utf-8'),
            participants[7][0].encode('utf-8'),participants[8][0].encode('utf-8'), participants[9][0].encode('utf-8'), ))
        # print '%d Inserted.' % match_id
    # Code for update
    '''
        cursor.execute('UPDATE MatchChampion SET participant1=?, participant2=?, participant3=?,\
            participant4=?, participant5=?, participant6=?, participant7=?, participant8=?,participant9=?,\
            participant10=? WHERE match_id = ?', (participants[0][0].encode('utf-8'), participants[1][0].encode('utf-8'),
            participants[2][0].encode('utf-8'), participants[3][0].encode('utf-8'), participants[4][0].encode('utf-8'),
            participants[5][0].encode('utf-8'), participants[6][0].encode('utf-8'), participants[7][0].encode('utf-8'),
            participants[8][0].encode('utf-8'), participants[9][0].encode('utf-8'), item[0],))
    '''

    print('Done.\nElapsed time: %.2fs.\n' % (time.time()-st))

    cursor.close()
    conn.commit()
    conn.close()

'''
Update ChampionMatchStats' kdas and damages:
1. SELECT sum(kills), sum(deaths), ... FROM Participant WHERE champion = ...
2. INSERT INTO ChampionMatchStats VALUES(kills, deaths, ..)
3. UPDATE ChampionMatchStats SET picks = ?, bans = ? WHERE champion = ?
'''
def champion_match_stats_to_sqlite():
    # TODO: champion dynamic enumeration using select distinct(champion) from participant
    conn = sqlite3.connect('lola.db')
    cursor = conn.cursor()

    print('Updating champion stats of matches to ChampionMatchStats...')
    # Select kda, damages, wards... of every champions
    st = time.time()
    for champion in champions:
        cursor.execute('SELECT champion FROM ChampionMatchStats WHERE champion = ?', (champion,))
        exist = cursor.fetchone()
        if exist is None:
            print(champion)
            cursor.execute('SELECT sum(kills), sum(deaths), sum(assists), sum(gold_earned), sum(magic_damage_dealt_to_champions),\
                sum(physical_damage_dealt_to_champions), sum(true_damage_dealt_to_champions), sum(damage_taken),\
                sum(crowd_control_dealt), sum(ward_kills), sum(wards_placed) FROM Participant WHERE champion = ?', (champion, ))
            result = cursor.fetchone()
            # Insert part of champion stats, excluding picks/bans/wins and stats of team
            cursor.execute('INSERT INTO ChampionMatchStats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (champion,
                0, 0, 0, result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9],
                result[10], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None, None))
            # print champion, '\n', result
        # Update picks/bans/wins
        cursor.execute('SELECT COUNT(champion) FROM Participant WHERE champion = ?',(champion,))
        picks = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(ban) FROM TeamBan WHERE ban = ?',(champion,))
        bans = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(participant_win) FROM Participant WHERE champion = ?',(champion,))        
        wins = cursor.fetchone()[0]        
        cursor.execute('UPDATE ChampionMatchStats SET picks = ?, bans = ?, wins = ? WHERE champion = ?',(picks, bans, wins, champion,))

    print('Done.\nElapsed time: %.2fs\n' % (time.time() - st))

    cursor.close()
    conn.commit()
    conn.close()

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