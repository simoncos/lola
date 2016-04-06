import pandas as pd
import numpy as np
import sqlite3
import time
from itertools import groupby as g
from itertools import permutations 
 
'''
Announcement:
	1. At present the kill&assist matrix can only based on all data. We have finished the coding part of distribute with 
	avg_tier and version on both SQL and DataFrame. However both method is time consuming so we have not run it. 
	
'''

addr_db = 'C:/Users/Administrator/lola_merged.db'
ori_matrix = pd.DataFrame().fillna(0)
kill_matrix = pd.DataFrame().fillna(0)
assist_matrix = pd.DataFrame().fillna(0)

version = [] # contains all 11 version
all_version = []
tier = [] # contains all tier including 'UNRANKED'
all_matchid = [] # contains all matchid infor
avg_tier = [] # contains avg tier of all matches

def main(): # can only generate one Matrix once a time
	''' # extract kill assist matrix
	start_time = time.time()
	extract_Kill_infor()
	end_time = time.time()
	print 'Generate Kill Matrix costs: %.2fs' %(end_time-start_time)
	kill_matrix.to_csv('kill_matrix.csv')
	
	start_time = time.time()
	extract_Assist_infor()
	end_time = time.time()
	print 'Generate Assist Matrix costs: %.2fs' %(end_time-start_time)
	assist_matrix.to_csv('assist_matrix.csv')
	################alter table ChampionAssistMatrix rename column victim to assist
	
	start_time = time.time()
	assists_matrix_to_db(assist_matrix)
	end_time = time.time()
	print 'Assist Matrix to DB costs: %.2fs' %(end_time-start_time)

	start_time = time.time()
	kills_matrix_to_db(kill_matrix)
	end_time = time.time()
	print 'Kill Matrix to DB costs: %.2fs' %(end_time-start_time)
	'''

def extract_champions_to_dataframe():
	global ori_matrix
	conn = sqlite3.connect("SELECT DISTINCT(champion) FROM Participant")
	cursor = conn.execute("SELECT DISTINCT(champion) FROM Participant")
	temp = cursor.fetchall()
	temp_list = []
	for i in range(len(temp)):
		temp_list.append(temp[i][0])
	temp_list_T = list(np.array(temp_list).T)
	ori_matrix = pd.DataFrame(columns=temp_list, index=temp_list_T)
	kill_matrix = ori_matrix
	assist_matrix = ori_matrix
	conn.close()

def extract_Kill_infor():
	temp_happen = []
	global kill_matrix
	conn = sqlite3.connect(addr_db)
	cursor = conn.execute("SELECT match_id,happen,victim,killer from FrameKillEvent")
	i = 0
	for row in cursor:
		temp_happen.append(row[1])
		if i==0:
			temp_killer = row[3]
			temp_victim = row[2]
			kill_matrix.ix[temp_killer, temp_victim] += 1
			i += 1
		else:
			if not row[1]==temp_happen[i-1]:
				temp_killer = row[3]
				temp_victim = row[2]
				kill_matrix.ix[temp_killer, temp_victim] += 1
			i += 1

	conn.close()

def extract_Assist_infor():
	conn = sqlite3.connect(addr_db)
	cursor = conn.execute("SELECT killer,assist from FrameKillEvent") # consider the relationship between a&v or a&k?
	for row in cursor:
		if not row[1]==None:
			temp_assist = row[1]
			temp_killer = row[0]
			assist_matrix.ix[temp_assist, temp_killer] += 1 # row help column
	conn.close()

def assists_matrix_to_db(df):
	conn = sqlite3.connect(addr_db)
	temp_champions = list(df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT INTO ChampionAssistMatrix(killer,assist,assists) VALUES(?,?,?)",(i,j,df[j][i]))
		print '$-----Table:ChampionAssistMatrix Mission:assist infor-%s [Finished].-----$'%i
	conn.commit()
	conn.close()

def extract_assists_db_to_dataframe():
	conn = sqlite3.connect(addr_db)
	#new_matrix_assist = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
	global assist_matrix
	cursor = conn.execute("SELECT killer,assist,assists FROM ChampionAssistMatrix")
	for row in cursor:
		#new_matrix_assist.ix[row[1]][row[0]] = row[2] # row help column
		assist_matrix.ix[row[1]][row[0]] = row[2]
	conn.close()
	#return new_matrix_assist # this matrix is what you want

def kills_matrix_to_db(df):
	conn = sqlite3.connect(addr_db)
	temp_champions = list(df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT INTO ChampionKillMatrix(killer,victim,kills) VALUES(?,?,?)",(i,j,df[i][j]))
		print '$-----Table:ChampionKillMatrix Mission:kill infor-%s [Finished].-----$'%i
	conn.commit()
	conn.close()

def extract_kills_db_to_dataframe():
	conn = sqlite3.connect(addr_db)
	#new_matrix_kill = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
	global kill_matrix
	cursor = conn.execute("SELECT killer,victim,kills FROM ChampionKillMatrix")
	for row in cursor:
		#new_matrix_kill.ix[row[0]][row[1]] = row[2] # row kill column
		kill_matrix.ix[row[0]][row[1]] = row[2]
	conn.close()
	#return new_matrix_kill # this matrix is what you want
