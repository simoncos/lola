# -*- coding: utf-8 -*-
import time
import pandas as pd
import numpy as np
import sqlite3

# TODO: DECORATOR
def time_report():
	# start_time = time.time()
	# extract_Kill_infor()
	# end_time = time.time()
	# print 'Generate Kill Matrix costs: %.2fs' %(end_time-start_time)
	pass

def initial_matrix():
	'''
	initial champion-champion matrix, no direction
	'''
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT champion FROM ChampionMatchStats")
	temp = cursor.fetchall()
	conn.close()
	temp_list = []
	for i in range(len(temp)):
		temp_list.append(temp[i][0])
	temp_list_T = list(np.array(temp_list).T)
	initial_matrix_df = pd.DataFrame(columns=temp_list, index=temp_list_T).fillna(0)
	return initial_matrix_df

def kill_matrix():
	'''
	row: killer, column: victim
	'''
	kill_matrix_df = initial_matrix()
	temp_happen = []
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT match_id,happen,killer,victim from FrameKillEvent")
	i = 0
	# use the order of column (by match and happen) in the FrameKillEvent table
	# TODO: avoid using database record order, instead use match_id and happen to de-duplicate
	for row in cursor:
		temp_happen.append(row[1])
		if i==0:
			temp_killer = row[2]
			temp_victim = row[3]
			kill_matrix_df.ix[temp_killer, temp_victim] += 1
			i += 1
		else:
			if not row[1]==temp_happen[i-1]:
				temp_killer = row[2]
				temp_victim = row[3]
				kill_matrix_df.ix[temp_killer, temp_victim] += 1 # row kills column
			i += 1
	conn.close()
	kill_matrix_df.to_csv('kill_matrix.csv')
	return kill_matrix_df

def assist_matrix():
	'''
	row: killer, column: assist
	'''
	assist_matrix_df = initial_matrix()
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT killer,assist from FrameKillEvent") # consider the relationship between a&v or a&k?
	for row in cursor:
		if not row[1]==None:
			temp_killer = row[0]
			temp_assist = row[1]
			assist_matrix_df.ix[temp_assist, temp_killer] += 1 # row helps column
	conn.close()
	assist_matrix_df.to_csv('assist_matrix.csv')
	return assist_matrix_df

def kill_matrix_to_sqlite():
	kill_matrix_df = kill_matrix()
	conn = sqlite3.connect('lola.db')
	temp_champions = list(kill_matrix_df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT OR REPLACE INTO ChampionKillMatrix(killer,victim,kills) VALUES(?,?,?)",(i,j,int(kill_matrix_df[j][i])))
		print('$-----Table:ChampionKillMatrix Mission:kill infor-%s [Finished].-----$'%i)
	conn.commit()
	conn.close()

def assist_matrix_to_sqlite(assist_matrix_df):
	assist_matrix_df = assist_matrix()
	conn = sqlite3.connect('lola.db')
	temp_champions = list(assist_matrix_df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT OR REPLACE INTO ChampionAssistMatrix(killer,assist,assists) VALUES(?,?,?)",(i,j,int(assist_matrix_df[i][j])))
		print('$-----Table:ChampionAssistMatrix Mission:assist infor-%s [Finished].-----$'%i)
	conn.commit()
	conn.close()

def sqlite_to_kill_matrix(norm=None):
	'''
	read champion kill matrix from database
	norm: None / 'picks'
	'''
	kill_matrix_df = initial_matrix()
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT killer,victim,kills FROM ChampionKillMatrix")
	for row in cursor:
		kill_matrix_df.ix[row[0]][row[1]] = row[2]
	conn.close()
	if norm == 'picks':
		kill_matrix_df = matrix_norm_by_pick(kill_matrix_df)
	return kill_matrix_df

def sqlite_to_death_matrix(norm=None):
	death_matrix_df = sqlite_to_kill_matrix(norm).transpose()
	return death_matrix_df

def sqlite_to_assist_matrix(norm=None):
	'''
	read champion assist matrix from database
	norm: None / 'picks'
	'''
	assist_matrix_df = initial_matrix()
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT killer,assist,assists FROM ChampionAssistMatrix")
	for row in cursor:
		assist_matrix_df.ix[row[1]][row[0]] = row[2]
	conn.close()
	if norm == 'picks':
		assist_matrix_df = matrix_norm_by_pick(assist_matrix_df)
	return assist_matrix_df

def matrix_norm_by_pick(matrix_df):
	conn = sqlite3.connect('lola.db')
	pick_ban_info = pd.read_sql("SELECT champion,picks,bans FROM ChampionMatchStats", conn, index_col=['champion'])
	conn.close()
	pick_infor_matrix = pick_ban_info['picks']
	normed_matrix = matrix_df.divide(pick_infor_matrix, axis='index')
	return(normed_matrix)

# TODO: normalized matrix in sqlite_to_assist_matrix / sqlite_to_kill_matrix

''' TODO:devided matrix by version and avg_tier
def AM_table():
	conn = sqlite3.connect('lola.db')
	temp = conn.execute('SELECT DISTINCT(champion) FROM Participant')
	c = [] # c[]: a list of 128 champions
	cc = [] # permutation sized 127*127
	for i in temp.fetchall():
		c.append(i[0]) 
	cc = permutations(c,2)
	
	for i in range(len(version)):
		for j in range(len(tier)):
			#for k in cc:
			for q in range(len(c)):
				t = conn.execute("SELECT count(*) FROM FrameKillEvent WHERE version=? AND avg_tier=? AND killer=? AND assist=?",(version[i],tier[j],'Vayne',c[q]))#k[0],k[1]
				conn.execute("INSERT INTO AM_Table VALUES(?,?,?,?,?)",(version[i],tier[j],'Vayne',c[q],t.fetchall()[0][0]))#k[0],k[1]
				t = conn.execute("SELECT count(*) FROM FrameKillEvent WHERE version=? AND avg_tier=? AND killer=? AND assist=?",(version[i],tier[j],'Vayne',c[q]))#k[0],k[1]
				print 'Hero:%s--%s  Num:%d'%('Vayne',c[q],t.fetchall()[0][0]) #k[0],k[1]
			print '$-----Table:AM_table Mission:Tier-%s [Finished].-----$' %tier[j]
		print '$-----Table:AM_table Mission:Version-%s [Finished].-----$' %version[i]
	conn.commit()
	conn.close()
'''