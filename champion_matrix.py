# -*- coding: utf-8 -*-
"""
LoLa champion relationship matrix
"""
import time
import pandas as pd
import numpy as np
import sqlite3
import itertools

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
    # TODO: champion static data
    cursor = conn.execute("SELECT champion FROM ChampionMatchStats")
    champions = cursor.fetchall()
    conn.close()
    champion_list = []
    for i in range(len(champions)):
        champion_list.append(champions[i][0])
    initial_matrix_df = pd.DataFrame(
        0, columns=champion_list, index=champion_list, dtype=int
    )
    return initial_matrix_df

def kill_matrix():
    '''
    row: killer, column: victim
    '''
    kill_matrix_df = initial_matrix()
    conn = sqlite3.connect('lola.db')
    # FrameKillEvent contains one row per assist. Count each logical kill once,
    # without treating timestamps from different matches as the same event.
    cursor = conn.execute(
        "SELECT DISTINCT match_id,happen,killer,victim FROM FrameKillEvent"
    )
    for row in cursor:
        killer = row[2]
        victim = row[3]
        kill_matrix_df.loc[killer, victim] += 1 # row kills column
    conn.close()
    kill_matrix_df.to_csv('kill_matrix.csv')
    return kill_matrix_df

def assist_matrix():
    '''
    row: assist, column: killer
    '''
    assist_matrix_df = initial_matrix()
    conn = sqlite3.connect('lola.db')
    cursor = conn.execute("SELECT killer,assist from FrameKillEvent") # consider the relationship between a&v or a&k?
    for row in cursor:
        if not row[1]==None:
            temp_killer = row[0]
            temp_assist = row[1]
            assist_matrix_df.loc[temp_assist, temp_killer] += 1 # row helps column
    conn.close()
    assist_matrix_df.to_csv('assist_matrix.csv')
    return assist_matrix_df

def incidence_matrices():
    conn = sqlite3.connect('lola.db')
    match_ids = pd.read_sql(
        "SELECT DISTINCT match_id FROM MatchChampion", conn
    )['match_id']

    counter_matrix = initial_matrix()
    partner_matrix = initial_matrix()

    count = 0
    print('processed match count:')
    for m in match_ids: # ten champions each match, combinations
        count += 1
        if count % 100 == 0:
            print(count)
        match_champions = conn.execute(
            "SELECT * FROM MatchChampion WHERE match_id = ?", (str(m),)
        ).fetchone()
        if match_champions is None:
            raise ValueError('Missing MatchChampion row for match {}'.format(m))
        champions = [
            value.decode('utf8') if isinstance(value, bytes) else value
            for value in match_champions[1:]
        ]
        champions_team_1 = champions[:5]
        champions_team_2 = champions[5:]

        for t in (champions_team_1, champions_team_2):
            for cp in itertools.combinations(t, 2):    
                partner_matrix.loc[cp[0], cp[1]] += 1
                partner_matrix.loc[cp[1], cp[0]] += 1

        for cc in itertools.product(champions_team_1, champions_team_2):
            counter_matrix.loc[cc[0], cc[1]] += 1
            counter_matrix.loc[cc[1], cc[0]] += 1

    conn.close()
    return counter_matrix, partner_matrix

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

def assist_matrix_to_sqlite(assist_matrix_df=None):
    if assist_matrix_df is None:
        assist_matrix_df = assist_matrix()
    conn = sqlite3.connect('lola.db')
    temp_champions = list(assist_matrix_df.columns)
    for i in temp_champions:
        for j in temp_champions:
            conn.execute("INSERT OR REPLACE INTO ChampionAssistMatrix(killer,assist,assists) VALUES(?,?,?)",(i,j,int(assist_matrix_df[i][j])))
        print('$-----Table:ChampionAssistMatrix Mission:assist infor-%s [Finished].-----$'%i)
    conn.commit()
    conn.close()

def incidence_matrices_to_sqlite():
    incidence_matrices_df = incidence_matrices()
    counter_matrix_df = incidence_matrices_df[0]
    partner_matrix_df = incidence_matrices_df[1]

    conn = sqlite3.connect('lola.db')
    temp_champions = list(counter_matrix_df.columns)
    for i in temp_champions:
        for j in temp_champions:
            conn.execute("INSERT OR REPLACE INTO ChampionIncidenceMatrix(champion_1,champion_2,counters, partners) VALUES(?,?,?,?)",(i, j, int(counter_matrix_df[j][i]), int(partner_matrix_df[j][i])))
        print('$-----Table:ChampionIncidenceMatrix Mission:inci infor-%s [Finished].-----$'%i)
    conn.commit()
    conn.close()

def sqlite_to_kill_matrix(norm=None):
    '''
    read champion kill matrix from database, Kill(i,j) means i kills j
    norm: None / 'picks'
    '''
    kill_matrix_df = initial_matrix()
    conn = sqlite3.connect('lola.db')
    cursor = conn.execute("SELECT killer,victim,kills FROM ChampionKillMatrix")
    for row in cursor:
        kill_matrix_df.loc[row[0], row[1]] = row[2]
    conn.close()
    if norm is None:
        return kill_matrix_df
    if norm == 'picks':
        return matrix_norm_by_pick(kill_matrix_df, 'row')
    raise ValueError('No such normalization method: {}'.format(norm))

def sqlite_to_death_matrix(norm=None):
    '''
    read champion death matrix from database, Death(i,j) means i is victim of j
    norm: None / 'picks'
    '''
    death_matrix_df = sqlite_to_kill_matrix().transpose() # D is K.transpose()
    if norm is None:
        return death_matrix_df
    if norm == 'picks':
        return matrix_norm_by_pick(death_matrix_df, 'row')
    raise ValueError('No such normalization method: {}'.format(norm))

def sqlite_to_assist_matrix(norm=None):
    '''
    read champion assist matrix from database, Assist(i,j) means i assists j
    norm: None / 'picks'
    '''
    assist_matrix_df = initial_matrix()
    conn = sqlite3.connect('lola.db')
    cursor = conn.execute("SELECT killer,assist,assists FROM ChampionAssistMatrix")
    for row in cursor:
        assist_matrix_df.loc[row[1], row[0]] = row[2]
    conn.close()
    if norm is None:
        return assist_matrix_df
    if norm == 'picks':
        return matrix_norm_by_pick(assist_matrix_df, 'row')
    raise ValueError('No such normalization method: {}'.format(norm))

def sqlite_to_incidence_matrix(relation):
    '''
    read champion incidence matrix from database, Incidence(i,j) means i and j are both picked (undirected)
    '''
    incidence_matrix_df = initial_matrix()
    conn = sqlite3.connect('lola.db')

    if relation == 'counter':
        cursor = conn.execute("SELECT champion_1,champion_2,counters FROM ChampionIncidenceMatrix")
        for row in cursor:
            incidence_matrix_df.loc[row[0], row[1]] = row[2]
            incidence_matrix_df.loc[row[1], row[0]] = row[2]
    elif relation == 'partner':
        cursor = conn.execute("SELECT champion_1,champion_2,partners FROM ChampionIncidenceMatrix")
        for row in cursor:
            incidence_matrix_df.loc[row[0], row[1]] = row[2]
            incidence_matrix_df.loc[row[1], row[0]] = row[2]
    else:
        conn.close()
        raise ValueError('No such incidence relation: {}'.format(relation))
    conn.close()
    return incidence_matrix_df

def dataframe_to_champion_matrix(matrix_df, norm):
    '''
    generate normalized champion matrix, numpy.ndarray
    '''
    if norm == None:
        champion_matrix = matrix_df.to_numpy(dtype=float)
    elif norm == 'row_pick':
        normed_matrix_df = matrix_norm_by_pick(matrix_df, 'row')
        champion_matrix = normed_matrix_df.to_numpy(dtype=float)
    elif norm == 'col_pick':
        normed_matrix_df = matrix_norm_by_pick(matrix_df, 'col')
        champion_matrix = normed_matrix_df.to_numpy(dtype=float)
    elif norm == 'counter_inci':
        champion_matrix = matrix_norm_by_incidence(matrix_df, 'counter')
    elif norm == 'partner_inci':
        champion_matrix = matrix_norm_by_incidence(matrix_df, 'partner')    
    else:
        raise ValueError('No such normalization method: {}'.format(norm))

    return champion_matrix

def matrix_norm_by_pick(matrix_df, direction):
    '''
    norm by picks of row champion
    '''
    conn = sqlite3.connect('lola.db')
    pick_ban_info = pd.read_sql("SELECT champion,picks,bans FROM ChampionMatchStats", conn, index_col=['champion'])
    conn.close()
    pick_infor_matrix_df = pick_ban_info['picks']
    if direction == 'row':
        normed_matrix_df = matrix_df.divide(pick_infor_matrix_df, axis='index') # no nan in normal cases
    elif direction == 'col':
        normed_matrix_df = matrix_df.divide(pick_infor_matrix_df, axis='columns')        
    return(normed_matrix_df)

def matrix_norm_by_incidence(matrix_df, relation): 
    '''
    norm by incidence of counter/partner pairs
    '''
    matrix = matrix_df.to_numpy(dtype=float)
    inci_matrix = sqlite_to_incidence_matrix(relation).to_numpy(dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        normed_matrix = np.divide(matrix, inci_matrix) # element-wise
    normed_matrix = np.nan_to_num(normed_matrix) # fill nan with 0
    return(normed_matrix)

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
