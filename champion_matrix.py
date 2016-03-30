import pandas as pd
import sqlite3
import time 

addr_db = 'lola_analysis_test.db'
addr_ori_matrix = 'K-Matrix.csv'
#addr_killmatrix_output = 'C:/Users/Administrator/Desktop/KA_matrix/K-Matrix-test.csv'
#addr_assistmatrix_output = 'C:/Users/Administrator/Desktop/KA_matrix/A-Matrix-test.csv'

ori_matrix = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
#assist_matrix = pd.read_csv(addr_assistmatrix_output, sep=',', header=0, index_col=0)

def main(): # can only generate one Matrix once a time
	
	#start_time = time.time()
	#extract_kill_infor()
	#end_time = time.time()
	#matrix_to_csv(df, addr_killmatrix_output)
	
	start_time = time.time()
	extract_assist_infor()
	end_time = time.time()
	print 'Generate Assist Matrix costs: %.2fs' %(end_time-start_time)
	
	assists_matrix_to_db(ori_matrix)
	print extract_assists_db_to_dataframe()


def extract_kill_infor():
	temp_happen = []
	conn = sqlite3.connect(addr_db)
	cursor = conn.execute("SELECT match_id,happen,victim,killer from FrameKillEvent")
	i = 0
	for row in cursor:
		temp_happen.append(row[1])
		if i==0:
			temp_killer = row[3]
			temp_victim = row[2]
			ori_matrix.ix[temp_killer, temp_victim] += 1
			i += 1
		else:
			if not row[1]==temp_happen[i-1]:
				temp_killer = row[3]
				temp_victim = row[2]
				ori_matrix.ix[temp_killer, temp_victim] += 1
			i += 1

	conn.close()

def extract_assist_infor():
	conn = sqlite3.connect(addr_db)
	cursor = conn.execute("SELECT killer,assist from FrameKillEvent") # consider the relationship between a&v or a&k?
	for row in cursor:
		if not row[1]==None:
			temp_assist = row[1]
			temp_killer = row[0]
			ori_matrix.ix[temp_killer, temp_assist] += 1
	conn.close()

# 4 functions for ZhaoChe
def assists_matrix_to_db(df):
	conn = sqlite3.connect(addr_db)
	temp_champions = list(df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT INTO ChampionAssistMatrix(killer,assist,assists) VALUES(?,?,?)",(i,j,df[i][j]))
	conn.commit()
	conn.close()

def extract_assists_db_to_dataframe(): #TODO: order of kill and assist!!!!
	conn = sqlite3.connect(addr_db)
	new_matrix_assist = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
	cursor = conn.execute("SELECT killer,assist,assists FROM ChampionAssistMatrix")
	for row in cursor:
		new_matrix_assist.ix[row[1]][row[0]] = row[2] # row help column
	conn.close()

	return new_matrix_assist # this matrix is what you want

def kills_matrix_to_db(df):
	conn = sqlite3.connect(addr_db)
	temp_champions = list(df.columns)
	for i in temp_champions:
		for j in temp_champions:
			conn.execute("INSERT INTO ChampionKillMatrix(killer,victim,kills) VALUES(?,?,?)",(i,j,df[i][j]))
	conn.commit()
	conn.close()

def extract_kills_db_to_dataframe():
	conn = sqlite3.connect(addr_db)
	new_matrix_kill = pd.read_csv(addr_ori_matrix, sep=',', header=0, index_col=0).fillna(0)
	cursor = conn.execute("SELECT killer,victim,kills FROM ChampionKillMatrix")
	for row in cursor:
		new_matrix_kill.ix[row[1]][row[0]] = row[2] # row kill column
	conn.close()

	return new_matrix_kill # this matrix is what you want

if __name__ == "__main__":
	main()


