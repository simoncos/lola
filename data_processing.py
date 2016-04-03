import sqlite3
import time
'''
1. Select a match
2. Select participants
3. Put into different sides
4. Sum up gold_earned, kills, assists,
	magic_damage, physical_damage, damage(above 3 are to champions),
	damage_taken, crowd_control_dealt,
	wards_placed, ward_kills
5. For each participants, normalize all above data by team's sums add to database
'''
def update_champion_stat(cursor, table, champion, field, increment):
	cursor.execute('SELECT {} FROM {} WHERE champion=?'.format(field, table), (champion,))
	tmp = cursor.fetchone()
	cursor.execute('UPDATE {} SET {}=? WHERE champion=?'.format(table, field), (tmp[0]+increment, champion,))

#All fields' name
fields = ['kills', 'deaths', 'assists', 'gold_earned', 'magic_damage', 'physical_damage', 'true_damage', 'damage_taken',
		'crowd_control_dealt', 'ward_kills', 'wards_placed']
fields_total = ['total_kills', 'total_deaths', 'total_assists', 'total_gold_earned','total_magic_damage',
		'total_physical_damage', 'total_true_damage', 'total_damage_taken', 'total_crowd_control_dealt','total_ward_kills',
		'total_wards_placed']

#Connect database
conn = sqlite3.connect('lola.db')
cursor = conn.cursor()

#Select matches
cursor.execute('SELECT match_id FROM Match')
matches = cursor.fetchall()

#Measure time
start_time = time.time()

for match in matches:
#Check if such match has been counted
	cursor.execute('SELECT * FROM CountedMatch WHERE match_id = ?', (match[0],))
	exist = cursor.fetchone()
	if exist is not None:
		continue
	else:
		print match[0]
		cursor.execute('INSERT INTO CountedMatch VALUES(?)', (match[0],))

#Go through participants' data
	blue_and_red = {'blue':[], 'red':[]}
	print 'Match ID:', int(match[0])
	cursor.execute('SELECT * FROM Participant WHERE match_id = ?', (match[0],))
	participants = cursor.fetchall()
	total = {'blue':{'kills':0, 'deaths':0, 'assists':0,'gold_earned':0, 'magic_damage':0,
		'physical_damage':0, 'true_damage':0, 'damage_taken':0, 'crowd_control_dealt':0, 'wards_placed':0,
		'ward_kills':0}, 
		'red':{'kills':0, 'deaths':0, 'assists':0,'gold_earned':0, 'magic_damage':0,
		'physical_damage':0, 'true_damage':0, 'damage_taken':0, 'crowd_control_dealt':0, 'wards_placed':0,
		'ward_kills':0}}
	for participant in participants:
		tmp = {}
		side = participant[3].encode('utf-8')
		champion = participant[4].encode('utf-8')
		kills = participant[9]
		deaths = participant[10]
		assists = participant[11]
		gold_earned = participant[19]
		magic_damage = participant[22]
		physical_damage = participant[25]
		true_damage = participant[28]
		damage_taken = participant[32]
		crowd_control_dealt = participant[35]
		ward_kills = participant[37]
		wards_placed = participant[38]
		tmp = {'side':side, 'champion':champion, 'kills':kills, 'deaths':deaths, 'assists':assists,
			'gold_earned':gold_earned, 'magic_damage':magic_damage, 'physical_damage':physical_damage,
			'true_damage':true_damage, 'damage_taken':damage_taken, 'crowd_control_dealt':crowd_control_dealt,
			'wards_placed':wards_placed, 'ward_kills':ward_kills}

#Put into different sides
		blue_and_red[side].append(tmp)

#Sum up total data for each sides
		total[side]['kills'] += kills
		total[side]['deaths'] += deaths
		total[side]['assists'] += assists
		total[side]['gold_earned'] += gold_earned
		total[side]['magic_damage'] += magic_damage
		total[side]['physical_damage'] += physical_damage
		total[side]['true_damage'] += true_damage
		total[side]['damage_taken'] += damage_taken
		total[side]['crowd_control_dealt'] += crowd_control_dealt
		total[side]['wards_placed'] += wards_placed
		total[side]['ward_kills'] += ward_kills

#Update stats to TotalChampionStats
	for player in blue_and_red['blue']:
		cursor.execute('SELECT * FROM TotalChampionStats WHERE champion = ?', (player['champion'],))
		exist = cursor.fetchone()
		if exist is not None:
		#Update
			for field in fields:
				update_champion_stat(cursor, 'TotalChampionStats', player['champion'], field, player[field])
			for field_total in fields_total:
				update_champion_stat(cursor, 'TotalChampionStats', player['champion'], field_total, total['blue'][field_total[6:]])
		else:
		#Insert
			cursor.execute('INSERT INTO TotalChampionStats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',\
				(player['champion'],player['kills'],player['deaths'],player['assists'],player['gold_earned'],player['magic_damage'],\
					player['physical_damage'],player['true_damage'], player['damage_taken'],\
					player['crowd_control_dealt'],player['ward_kills'],player['wards_placed'],total['blue']['kills'],\
					total['blue']['deaths'],total['blue']['assists'],total['blue']['gold_earned'],total['blue']['magic_damage'],\
					total['blue']['physical_damage'],total['blue']['true_damage'],total['blue']['damage_taken'],\
					total['blue']['crowd_control_dealt'],total['blue']['ward_kills'],total['blue']['wards_placed']))
	for player in blue_and_red['red']:
		cursor.execute('SELECT * FROM TotalChampionStats WHERE champion = ?', (player['champion'],))
		exist = cursor.fetchone()
		if exist is not None:
		#Update
			for field in fields:
				update_champion_stat(cursor, 'TotalChampionStats', player['champion'], field, player[field])
			for field_total in fields_total:
				update_champion_stat(cursor, 'TotalChampionStats', player['champion'], field_total, total['blue'][field_total[6:]])
		else:
		#Insert
			cursor.execute('INSERT INTO TotalChampionStats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',\
				(player['champion'],player['kills'],player['deaths'],player['assists'],player['gold_earned'],player['magic_damage'],\
					player['physical_damage'],player['true_damage'], player['damage_taken'],\
					player['crowd_control_dealt'],player['ward_kills'],player['wards_placed'],total['red']['kills'],\
					total['red']['deaths'],total['red']['assists'],total['red']['gold_earned'],total['red']['magic_damage'],\
					total['red']['physical_damage'],total['red']['true_damage'],total['red']['damage_taken'],\
					total['red']['crowd_control_dealt'],total['red']['ward_kills'],total['red']['wards_placed']))

cursor.execute('SELECT * FROM TotalChampionStats')
result = cursor.fetchall()
for item in result:
	print item
cursor.execute('SELECT * FROM CountedMatch')
result = cursor.fetchall()
print result

#Print elapased time, 22276s for 50000
print "Elapsed time:", time.time() - start_time

cursor.close()
conn.commit()
conn.close()