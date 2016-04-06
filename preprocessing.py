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

# TODO: ChampionMatchStats and ChampionRank Initialization (insert or ignore)
# TODO: average tier