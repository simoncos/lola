import sqlite3
import time

'''
Update MatchChampion:
1. SELECT match_id FROM Match
2. SELECT champion FROM Participant WHERE match_id = ? ORDER BY participant_id
3. INSERT INTO MatchChampion VALUES(match_id, participant1, ...)
'''
def match_champion_to_sqlite():
	conn = sqlite3.connect('lola.db')
	cursor = conn.cursor()

	# Select uncounted match_ids
	cursor.execute('SELECT match_id FROM Match')
	result = cursor.fetchall()

	st = time.time()
	for item in result:
	# Select champions of each match
		match_id = int(item[0].encode('utf-8'))
		cursor.execute('SELECT champion FROM Participant WHERE match_id = ? ORDER BY participant_id', (match_id,))
		champions = cursor.fetchall()
	# Insert champions into MatchChampion
		cursor.execute('INSERT INTO MatchChampion VALUES(?,?,?,?,?,?,?,?,?,?,?)', (match_id, champions[0][0].encode('utf-8'),
			champions[1][0].encode('utf-8'),champions[2][0].encode('utf-8'), champions[3][0].encode('utf-8'),
			champions[4][0].encode('utf-8'),champions[5][0].encode('utf-8'), champions[6][0].encode('utf-8'),
			champions[7][0].encode('utf-8'),champions[8][0].encode('utf-8'), champions[9][0].encode('utf-8'),))
		print '%d Inserted.' % match_id
	# Code for update
	'''
		cursor.execute('UPDATE CountedMatch SET participant1=?, participant2=?, participant3=?,\
			participant4=?, participant5=?, participant6=?, participant7=?, participant8=?,participant9=?,\
			participant10=? WHERE match_id = ?', (champions[0][0].encode('utf-8'), champions[1][0].encode('utf-8'),
			champions[2][0].encode('utf-8'), champions[3][0].encode('utf-8'), champions[4][0].encode('utf-8'),
			champions[5][0].encode('utf-8'), champions[6][0].encode('utf-8'), champions[7][0].encode('utf-8'),
			champions[8][0].encode('utf-8'), champions[9][0].encode('utf-8'), item[0],))
	'''

	print 'Elapsed time: %.2fs' % (time.time()-st)

	cursor.close()
	conn.commit()
	conn.close()

if __name__=='__main__':
	match_champion_to_sqlite()