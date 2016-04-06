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

def AM_table():
	conn = sqlite3.connect(addr_db)
	"""
	conn.execute('''CREATE TABLE `AM_Table` (
	-- `id`	integer NOT NULL,
					`version`	text ,	
					`avg_tier`	text ,
					`killer`	text NOT NULL,
					`assist`	text NOT NULL,
					`assists`	integer NOT NULL
		-- PRIMARY KEY(id)
				);''')
	conn.commit()
	print '$-----Table:AM_table Mission:Table Creation [Finished].-----$'
	"""

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

#-----win rate of top5 ban and pick-----#
def top_banpick_win():
	conn = sqlite3.connect(addr_db)
	win_rate_matrix = []
	pick_ban_infor = pd.read_sql("SELECT champion,picks,bans FROM Champion", conn, index_col=['champion'])
	top_ten_pick_infor = pick_ban_infor.sort('picks', ascending=False).iloc[0:10]
	top_ten_pick_champions = top_ten_pick_infor.index
	for i in top_ten_pick_champions:
		win = conn.execute("SELECT COUNT(champion) FROM Participant WHERE Participant.participant_win=1 and participant.champion=?",(i,))
		win = win.fetchone()[0]
		win_rate_matrix.append(float(win)/float(top_ten_pick_infor['picks'][i]))
	top_ten_pick_infor['win_rate'] = win_rate_matrix
	temp_series = pd.DataFrame(top_ten_pick_infor['win_rate'])
	#top_ten_pick_infor = # add a new column then insert win_rate into it , then draw the image with name and win_rate
	plt_pick = temp_series.plot(kind='barh', title='Win Rate of Top 10', stacked=False).set_xlabel('Proportion').get_figure()
	plt_pick.savefig('C:\\Users\\Administrator\\Desktop\\win_rate_pick_Top_10.png')
	
	win_rate_matrix = []
	top_ten_ban_infor = pick_ban_infor.sort('bans', ascending=False).iloc[0:10]
	top_ten_ban_champions = top_ten_ban_infor.index
	for i in top_ten_ban_champions:
		win = conn.execute("SELECT COUNT(champion) FROM Participant WHERE Participant.participant_win=1 and participant.champion=?",(i,))
		win = win.fetchone()[0]
		win_rate_matrix.append(float(win)/float(top_ten_ban_infor['picks'][i]))
	top_ten_ban_infor['win_rate'] = win_rate_matrix
	temp_series = pd.DataFrame(top_ten_ban_infor['win_rate'])
	#top_ten_pick_infor = # add a new column then insert win_rate into it , then draw the image with name and win_rate
	plt_ban = temp_series.plot(kind='barh', title='Win Rate of Top 10', stacked=False).set_xlabel('Proportion').get_figure()
	plt_ban.savefig('C:\\Users\\Administrator\\Desktop\\win_rate_ban_Top_10.png')


def win_rate():
	conn = sqlite3.connect(addr_db)
	win_rate_matrix = []
	pick_ban_infor = pd.read_sql("SELECT champion,picks,bans FROM Champion", conn, index_col=['champion'])
	all_pick_infor = pick_ban_infor.sort('picks', ascending=False)
	all_pick_champions = all_pick_infor.index
	for i in all_pick_champions:
		win = conn.execute("SELECT COUNT(champion) FROM Participant WHERE Participant.participant_win=1 and participant.champion=?",(i,))
		win = win.fetchone()[0]
		win_rate_matrix.append(float(win)/float(all_pick_infor['picks'][i]))
	all_pick_infor['win_rate'] = win_rate_matrix
	temp_series = pd.DataFrame(all_pick_infor['win_rate']).sort('win_rate', ascending=False)
	#top_ten_pick_infor = # add a new column then insert win_rate into it , then draw the image with name and win_rate
	plt_all = temp_series.plot(kind='barh', title='Win Rate of Top 10', stacked=False).set_xlabel('Proportion').get_figure()
	plt_all.savefig('C:\\Users\\Administrator\\Desktop\\Top10_win_rate.png')
	conn.close()

if __name__ == "__main__":
	main()

