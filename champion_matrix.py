# -*- coding: utf-8 -*-
import time
import pandas as pd
import numpy as np
import sqlite3

def time_report(): #TODO: DECORATOR
	# start_time = time.time()
	# extract_Kill_infor()
	# end_time = time.time()
	# print 'Generate Kill Matrix costs: %.2fs' %(end_time-start_time)
	pass

def initial_matrix():
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT champion FROM ChampionMatchStats") #TODO
	temp = cursor.fetchall()
	temp_list = []
	for i in range(len(temp)):
		temp_list.append(temp[i][0])
	temp_list_T = list(np.array(temp_list).T)
	initial_matrix_df = pd.DataFrame(columns=temp_list, index=temp_list_T)
	conn.close()
	return initial_matrix_df

def kill_matrix(initial_matrix_df):
	kill_matrix_df = initial_matrix_df
	temp_happen = []
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT match_id,happen,victim,killer from FrameKillEvent")
	i = 0
	for row in cursor:
		temp_happen.append(row[1])
		if i==0:
			temp_killer = row[3]
			temp_victim = row[2]
			kill_matrix_df.ix[temp_killer, temp_victim] += 1
			i += 1
		else:
			if not row[1]==temp_happen[i-1]:
				temp_killer = row[3]
				temp_victim = row[2]
				kill_matrix_df.ix[temp_killer, temp_victim] += 1
			i += 1
	conn.close()
	kill_matrix_df.to_csv('kill_matrix.csv')

def assist_matrix(initial_matrix_df):
	assist_matrix_df = initial_matrix_df
	conn = sqlite3.connect('lola.db')
	cursor = conn.execute("SELECT killer,assist from FrameKillEvent") # consider the relationship between a&v or a&k?
	for row in cursor:
		if not row[1]==None:
			temp_assist = row[1]
			temp_killer = row[0]
			assist_matrix_df.ix[temp_assist, temp_killer] += 1 # row help column
	conn.close()
	assist_matrix_df.to_csv('assist_matrix.csv')

def kill_matrix_to_sqlite(kill_matrix_df):
	conn = sqlite3.connect('lola.db')
	temp_champions = list(kill_matrix_df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT INTO ChampionKillMatrix(killer,victim,kills) VALUES(?,?,?)",(i,j,kill_matrix_df[i][j]))
		print('$-----Table:ChampionKillMatrix Mission:kill infor-%s [Finished].-----$'%i)
	conn.commit()
	conn.close()

def assist_matrix_to_sqlite(assist_matrix_df):
	conn = sqlite3.connect('lola.db')
	temp_champions = list(assist_matrix_df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT INTO ChampionAssistMatrix(killer,assist,assists) VALUES(?,?,?)",(i,j,assist_matrix_df[j][i]))
		print('$-----Table:ChampionAssistMatrix Mission:assist infor-%s [Finished].-----$'%i)
	conn.commit()
	conn.close()

def sqlite_to_assist_matrix(initial_matrix_df):
	assist_matrix_df = initial_matrix_df
	conn = sqlite3.connect('lola.db')
	#new_matrix_assist = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
	cursor = conn.execute("SELECT killer,assist,assists FROM ChampionAssistMatrix")
	for row in cursor:
		#new_matrix_assist.ix[row[1]][row[0]] = row[2] # row help column
		assist_matrix_df.ix[row[1]][row[0]] = row[2]
	conn.close()
	return assist_matrix_df

def sqlite_to_kill_matrix(initial_matrix_df):
	kill_matrix_df = initial_matrix_df
	conn = sqlite3.connect('lola.db')
	#new_matrix_kill = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
	cursor = conn.execute("SELECT killer,victim,kills FROM ChampionKillMatrix")
	for row in cursor:
		#new_matrix_kill.ix[row[0]][row[1]] = row[2] # row kill column
		kill_matrix_df.ix[row[0]][row[1]] = row[2]
	conn.close()
	return kill_matrix_df

# TODO: normalized matrix in sqlite_to_assist_matrix / sqlite_to_kill_matrix
# TODO: matrix by version and average tier