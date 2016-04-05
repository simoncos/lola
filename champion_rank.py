# -*- coding: utf-8 -*-
"""
LoLa data crawling based on Cassiopeia.
"""
import pandas as pd
import numpy as np
from scipy import spatial
from scipy.sparse import linalg
import scipy.linalg
import networkx as nx

def print_full(df): 
	'''
	print all rows of pd.DataFrame
	'''
	pd.set_option('display.max_rows', len(df))
	print(df)
	pd.reset_option('display.max_rows')

# for testing
def main():
	#champion_matrix_rank()

def champion_pick_rank():
    pass

def champion_win_rank():
	pass

def champion_ban_rank():
	pass 

def champion_distribution(champion_matrix_df, champion): #TODO
	vector = champion_matrix_df.ix[champion]
	values, base = np.histogram(vector, bins=40)
	plt.plot(values)

def champion_cosine_similarity(champion_matrix_df, champion_1, champion_2): #TODO
	return 1 - spatial.distance.cosine(champion_matrix_df.ix[champion_1], champion_matrix_df.ix[champion_2])

def champion_matrix_rank(champion_matrix_df, criteron, norm=False): #TODO:df should be changedm1atrix
	'''
	champion_matrix_df: pd.DataFrame, kill/death/assist counts between champions, 
						(a,b)=i means a kills / killed by / assists b for i times 
	criteron: 'count', 'eigen', 'eigen_ratio', 'eigen_diff', 'pagerank', 'hits' 
	norm: True, False
	'''
	champion_matrix = champion_matrix_df.as_matrix()
	
	if norm == True:
		row_sum = champion_matrix.sum(axis=1)
		champion_matrix = champion_matrix / row_sum[:, numpy.newaxis] # pandas broadcast

	# Count
	if criteron == 'count':
		print("Champion Rank by counts:")
		rank_df = pd.DataFrame()
		rank_df['champion'] = pd.Series(champion_matrix_df.index)
		rank_df['count'] = champion_matrix.sum(axis=1)
		print_full(rank_df.sort_values(by='count', ascending=False))

	# ED
	elif criteron == 'eigen':
		print("Champion Rank by eigenvector centrality")
		rank_df = pd.DataFrame()
		rank_df['champion'] = pd.Series(champion_matrix_df.index)
		# eigenvector with largest eigenvalue (k=1), sometimes all negative, sometimes all positive, absolute values unchanged
		rank_df['eigen_1'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=1)[1]))
		print_full(rank_df.sort_values(by='eigen_1', ascending=False))

		#rank_df['eigen_2'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=2)[1][:,1]))		
		#print_full(rank_df.sort_values(by='eigen_2', ascending=False))

	# ED Ratio, eigen(M)/eigen(M.T)
	elif criteron == 'eigen_ratio':
		print("Champion Rank by eigenvector centrality ratio")
		rank_df = pd.DataFrame()
		rank_df['champion'] = pd.Series(champion_matrix_df.index)
		rank_df['eigen'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=1)[1]))
		rank_df['eigen_t'] = pd.DataFrame(abs(linalg.eigs(champion_matrix.transpose(), k=1)[1]))
		rank_df['eigen_ratio'] = rank_df['eigen'] / rank_df['eigen_t']
		print_full(rank_df.sort_values(by='eigen_ratio', ascending=False))	

	# ED Diff, eigen(M)-eigen(M.T)
	elif criteron == 'eigen_diff':
		print("Champion Rank by eigenvector centrality difference")
		rank_df = pd.DataFrame()
		rank_df['champion'] = pd.Series(champion_matrix_df.index)
		rank_df['eigen'] = pd.DataFrame(abs(linalg.eigs(champion_matrix, k=1)[1]))
		rank_df['eigen_t'] = pd.DataFrame(abs(linalg.eigs(champion_matrix.transpose(), k=1)[1]))
		rank_df['eigen_diff'] = rank_df['eigen'] - rank_df['eigen_t']
		print_full(rank_df.sort_values(by='eigen_diff', ascending=False))	

	# PageRank: similar result with eigenvector centrality
	elif criteron == 'pagerank':
		print("Champion Rank by PageRank")
		G = nx.to_networkx_graph(champion_matrix)
		pr = nx.pagerank(G)
		rank_df = pd.DataFrame()
		rank_df['champion'] = pd.Series(champion_matrix_df.index)
		rank_df['pagerank'] = pd.DataFrame(data=list(pr.values()), index=list(pr.keys()))
		print_full(rank_df.sort_values(by='pagerank', ascending=False))	

	# HITS: hub=auth
	elif criteron == 'hits':
		print("Champion Rank by HITS")
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

if __name__ == '__main__':
	main()