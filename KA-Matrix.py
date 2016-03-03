import pandas as pd
import sqlite3
import time 

addr_Database = 'C:/Users/Administrator/lola.db'
addr_Ori_Matrix = 'C:/Users/Administrator/Desktop/KA_matrix/K-Matrix.csv'
addr_KillMatrix_output = 'C:/Users/Administrator/Desktop/KA_matrix/K-Matrix-test.csv'
addr_AssistMatrix_output = 'C:/Users/Administrator/Desktop/KA_matrix/A-Matrix-test.csv'

df = pd.read_csv(addr_Ori_Matrix, sep=',', header=0, index_col=0)
df = df.fillna(0)

def main(): # can only generate one Matrix once a time
	start_time = time.time()
	extract_Kill_infor()
	end_time = time.time()
	matrix_to_csv(df, addr_KillMatrix_output)
	#start_time = time.time()
	#extract_Assist_infor()
	#end_time = time.time()
	#matrix_to_csv(df, addr_AssistMatrix_output)
	print 'Generate Assist Matrix costs: %.2fs' %(end_time-start_time)

def extract_Kill_infor():
	temp_happen = []
	conn = sqlite3.connect(addr_Database)
	cursor = conn.execute('SELECT match_id,happen,victim,killer from FrameKillEvent')
	i = 0
	for row in cursor:
		temp_happen.append(row[1])
		if i==0:
			temp_killer = row[3]
			temp_victim = row[2]
			df.ix[temp_killer, temp_victim] += 1
			i += 1
		else:
			if not row[1]==temp_happen[i-1]:
				temp_killer = row[3]
				temp_victim = row[2]
				df.ix[temp_killer, temp_victim] += 1
				i += 1
		#if i>=12:
		#	break
	
#df.ix['Karma','Lee Sin'] should be 2
#df.ix['Ahri','Karma'] should be 1
	conn.close()

def extract_Assist_infor():
	conn = sqlite3.connect(addr_Database)
	cursor = conn.execute('SELECT killer,assist from FrameKillEvent') # consider the relationship between a&v or a&k?
	#i = 0
	for row in cursor:
		if not row[1]==None:
			temp_assist = row[1]
			temp_killer = row[0]
			df.ix[temp_killer, temp_assist] += 1
		#i += 1
		#if i>10:
		#	break

#df.ix['Ahri','Lee Sin'] should be 1
#df.ix['Tristana','Nami'] should be 2
	conn.close()

def matrix_to_csv(df, output_addr):
	df.to_csv(output_addr)


	'''
	for row in cursor:
		if i<10:
			print 'match_id', row[0]
			print 'happen', row[1]
			print 'victim', row[2]
			print 'killer', row[3], '\n'
			i += 1
			# df.ix['Aatrox', 'Aatrox']
	'''


if __name__ == "__main__":
	main()



"""
def extract():
	conn = sqlite3.connect('lola_null.db')
	print 'connect 1'
	conn.execute('''CREATE TABLE KA_MATRIX
		(
			match_id	text NOT NULL,
			happen	int NOT NULL, 
			kill_count	int NOT NULL,
			assist_count	int NOT NULL,
			champion_level	integer NOT NULL 
		);''') 
	print 'create table 1'
	conn.close()
"""
