import sqlite3
import time

conn = sqlite3.connect('lola.db')
cursor = conn.cursor()

cursor.execute('SELECT match_id, participant1 FROM CountedMatch  LIMIT -1 Offset 40000')
result = cursor.fetchall()

st = time.time()
for item in result:
	if item[1] is None:
		print item[0]
		cursor.execute('SELECT champion FROM Participant WHERE match_id = ? ORDER BY participant_id', (item[0],))
		champions = cursor.fetchall()
		cursor.execute('UPDATE CountedMatch SET participant1=?, participant2=?, participant3=?,\
			participant4=?, participant5=?, participant6=?, participant7=?, participant8=?,participant9=?,\
			participant10=? WHERE match_id = ?', (champions[0][0].encode('utf-8'), champions[1][0].encode('utf-8'),
			champions[2][0].encode('utf-8'), champions[3][0].encode('utf-8'), champions[4][0].encode('utf-8'),
			champions[5][0].encode('utf-8'), champions[6][0].encode('utf-8'), champions[7][0].encode('utf-8'),
			champions[8][0].encode('utf-8'), champions[9][0].encode('utf-8'), item[0],))

print 'Elapsed time: %.2fs' % (time.time()-st)
cursor.close()
conn.commit()
conn.close()