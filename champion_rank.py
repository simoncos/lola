# -*- coding: utf-8 -*-
"""
LoLa champion ranking
"""
import pandas as pd
import numpy as np
from scipy import spatial
from scipy.sparse import linalg
import networkx as nx
import matplotlib.pyplot as plt
import champion_matrix as lola # TODO: lola library namespace
\n
def print_full(df): 
    '''
    print all rows of pd.DataFrame
    '''
    pd.set_option('display.max_rows', len(df))
    print('\n')
    print(df)
    pd.reset_option('display.max_rows')

# TODO:
def champion_win_rate_rank():
    pass

def champion_pick_rate_rank():
    pass

def champion_ban_rate_rank():
    pass 

def champion_average_kda_rank():
    pass

def champion_distribution(champion_matrix_df, champion): #TODO
    vector = champion_matrix_df.ix[champion]
    values, base = np.histogram(vector, bins=40)
    plt.plot(values)

def champion_cosine_similarity(champion_matrix_df, champion_1, champion_2): #TODO
    return 1 - spatial.distance.cosine(champion_matrix_df.ix[champion_1], champion_matrix_df.ix[champion_2])

def champion_matrix_rank(champion_matrix_df, criteron, norm=None, row_sum_norm=False):
    '''
    champion_matrix_df: pd.DataFrame, kill/death/assist counts between champions, 
                        (a,b)=i means a kills / killed by / assists b for i times 
    criteron: 'sum', 'eigen', 'eigen_ratio', 'eigen_diff', 'pagerank', 'hits' 
    norm: row_pick, col_pick, counter_inci, partner_inci (K/D - counter; A - partner)
    row_sum_norm: row_sum norm without external information
    TODO: eigen_ratio and eigen_diff criteron can only be used in kill matrix, in assist do not make sense (would be forbidden in future)
    '''
    champion_matrix = lola.dataframe_to_champion_matrix(champion_matrix_df, norm)
    
    if row_sum_norm == True:
        row_sum = champion_matrix.sum(axis=1)
        champion_matrix = champion_matrix / row_sum[:, np.newaxis] # numpy broadcast    
        
    # Count
    if criteron == 'sum':
        print("Champion Rank by sum:")
        rank_df = pd.DataFrame()
        rank_df['champion'] = pd.Series(champion_matrix_df.index)
        rank_df['sum'] = champion_matrix.sum(axis=1) # row sum
        print_full(rank_df.sort_values(by='sum', ascending=False))

    # ED
    elif criteron == 'eigen':
        print("Champion Rank by eigenvector centrality")
        rank_df = pd.DataFrame()
        rank_df['champion'] = pd.Series(champion_matrix_df.index)
        # eigenvector with largest eigenvalue (k=1), sometimes all negative, sometimes all positive, absolute values unchanged
        rank_df['eigen_1'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=1)[1])) # matrix must be float for linalg.eigs 
        print_full(rank_df.sort_values(by='eigen_1', ascending=False))

        #rank_df['eigen_2'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=2)[1][:,1]))      
        #print_full(rank_df.sort_values(by='eigen_2', ascending=False))

    # ED Ratio, eigen(M)/eigen(M.T)
    elif criteron == 'eigen_ratio':
        print("Champion Rank by eigenvector centrality ratio:")
        rank_df = pd.DataFrame()
        rank_df['champion'] = pd.Series(champion_matrix_df.index)
        rank_df['eigen'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=1)[1]))
        rank_df['eigen_t'] = pd.DataFrame(abs(linalg.eigs(champion_matrix.transpose(), k=1)[1]))
        rank_df['eigen_ratio'] = rank_df['eigen'] / rank_df['eigen_t']
        print_full(rank_df.sort_values(by='eigen_ratio', ascending=False))  

    # ED Diff, eigen(M)-eigen(M.T)
    elif criteron == 'eigen_diff':
        print("Champion Rank by eigenvector centrality difference:")
        rank_df = pd.DataFrame()
        rank_df['champion'] = pd.Series(champion_matrix_df.index)
        rank_df['eigen'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=1)[1]))
        rank_df['eigen_t'] = pd.DataFrame(abs(linalg.eigs(champion_matrix.transpose(), k=1)[1]))
        rank_df['eigen_diff'] = rank_df['eigen'] - rank_df['eigen_t']
        print_full(rank_df.sort_values(by='eigen_diff', ascending=False))   

    # PageRank: similar results with eigenvector centrality
    elif criteron == 'pagerank':
        print("Champion Rank by PageRank:")
        G = nx.DiGraph(champion_matrix)
        pr = nx.pagerank(G)
        rank_df = pd.DataFrame()
        rank_df['champion'] = pd.Series(champion_matrix_df.index)
        rank_df['pagerank'] = pd.DataFrame(data=list(pr.values()), index=list(pr.keys()))
        print_full(rank_df.sort_values(by='pagerank', ascending=False)) 

    # HITS:
    elif criteron == 'hits':
        print("Champion Rank by HITS:")
        G = nx.DiGraph(champion_matrix)
        hub, auth = nx.hits(G)
        hub_rank_df = pd.DataFrame()
        hub_rank_df['champion'] = pd.Series(champion_matrix_df.index)
        hub_rank_df['hub'] = pd.DataFrame(data=list(hub.values()), index=list(hub.keys()))
        print_full(hub_rank_df.sort_values(by='hub', ascending=False))  
        auth_rank_df = pd.DataFrame()
        auth_rank_df['champion'] = pd.Series(champion_matrix_df.index)
        auth_rank_df['auth'] = pd.DataFrame(data=list(auth.values()), index=list(auth.keys()))
        print_full(auth_rank_df.sort_values(by='auth', ascending=False))    

    else:
        raise ValueError('Invalid criteron provided.')

'''
TODO: Visualization Part

def top_banpick_win():
    conn = sqlite3.connect('lola.db')
    win_rate_matrix = []
    pick_ban_infor = pd.read_sql("SELECT champion,picks,bans FROM ChampionMatchStats", conn, index_col=['champion'])
    top_ten_pick_infor = pick_ban_infor.sort_values(by='picks', ascending=False).iloc[0:10]
    top_ten_pick_champions = top_ten_pick_infor.index
    for i in top_ten_pick_champions:
        win = conn.execute("SELECT COUNT(champion) FROM Participant WHERE Participant.participant_win=1 and participant.champion=?",(i,))
        win = win.fetchone()[0]
        win_rate_matrix.append(float(win)/float(top_ten_pick_infor['picks'][i]))
    top_ten_pick_infor['win_rate'] = win_rate_matrix
    temp_series = pd.DataFrame(top_ten_pick_infor['win_rate']).sort_values(by='win_rate', ascending=True) # inverse the order
    # top_ten_pick_infor = # add a new column then insert win_rate into it , then draw the image with name and win_rate
    plt_pick = temp_series.plot(kind='barh', title='Win Rate of Pick Top 10 Champion', stacked=False).set_xlabel('Proportion').get_figure()
    # plt_pick.savefig('win_rate_pick_Top_10.png')
    
    win_rate_matrix = []
    top_ten_ban_infor = pick_ban_infor.sort_values(by='bans', ascending=False).iloc[0:10]
    top_ten_ban_champions = top_ten_ban_infor.index
    for i in top_ten_ban_champions:
        win = conn.execute("SELECT COUNT(champion) FROM Participant WHERE Participant.participant_win=1 and participant.champion=?",(i,))
        win = win.fetchone()[0]
        win_rate_matrix.append(float(win)/float(top_ten_ban_infor['picks'][i]))
    conn.close()
    top_ten_ban_infor['win_rate'] = win_rate_matrix
    temp_series = pd.DataFrame(top_ten_ban_infor['win_rate']).sort_values(by='win_rate', ascending=True) # inverse the order
    #top_ten_pick_infor = # add a new column then insert win_rate into it , then draw the image with name and win_rate
    plt_ban = temp_series.plot(kind='barh', title='Win Rate of Ban Top 10 Champion', stacked=False).set_xlabel('Proportion').get_figure()
    # plt_ban.savefig('win_rate_ban_Top_10.png')


def win_rate():
    conn = sqlite3.connect('lola.db')
    win_rate_matrix = []
    pick_ban_infor = pd.read_sql("SELECT champion,picks,bans FROM ChampionMatchStats", conn, index_col=['champion'])
    all_pick_infor = pick_ban_infor.sort_values(by='picks', ascending=False)
    all_pick_champions = all_pick_infor.index
    for i in all_pick_champions:
        win = conn.execute("SELECT COUNT(champion) FROM Participant WHERE Participant.participant_win=1 and participant.champion=?",(i,))
        win = win.fetchone()[0]
        win_rate_matrix.append(float(win)/float(all_pick_infor['picks'][i]))
    conn.close()
    all_pick_infor['win_rate'] = win_rate_matrix
    temp_series = pd.DataFrame(all_pick_infor['win_rate']).sort_values(by='win_rate', ascending=True)
    # top_ten_pick_infor = # add a new column then insert win_rate into it , then draw the image with name and win_rate
    plt_all = temp_series.plot(kind='barh', title='Win Rate Rank', stacked=False).set_xlabel('Proportion').get_figure()
    # plt_all.savefig('win_rate.png')
'''
