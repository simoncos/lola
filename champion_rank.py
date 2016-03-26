# -*- coding: utf-8 -*-
"""
LoLa data crawling based on Cassiopeia.
"""
import pandas as pd
from scipy.sparse import linalg
import scipy.linalg
import numpy 
import networkx as nx

def print_full(df): 
	'''
	print all rows of pd.DataFrame
	'''
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')

def main():
	champion_kill_rank()
	champion_assist_rank()

def champion_kill_rank(champion_kill_dataframe):
	
	champion_kill_matrix = champion_kill_dataframe.as_matrix()
	row_sum = champion_kill_matrix.sum(axis=1)
	champion_kill_matrix_norm = champion_kill_matrix / row_sum[:, numpy.newaxis] # broadcast

	# Count

	print("Champion Kill Rank by counts:")
	countkills = pd.DataFrame()
	countkills['champion'] = pd.Series(champion_kill_dataframe.index)
	countkills['kill_count'] = champion_kill_matrix.sum(axis=1)
	print_full(countkills.sort_values(by='kill_count', ascending=False))

	print("Champion Death Rank by counts:")
	countkills = pd.DataFrame()
	countkills['champion'] = pd.Series(champion_kill_dataframe.index)
	countkills['death_count'] = champion_kill_matrix.sum(axis=0)
	print_full(countkills.sort_values(by='death_count', ascending=False))

	# ED

	print("Champion Kill Rank by eigenvector centralities without normalization:")
	eigenkills = pd.DataFrame()
	eigenkills['champion'] = pd.Series(champion_kill_dataframe.index)
	# eigenvector with largest eigenvalue (k=1), sometimes all negative, sometimes all positive, absolute values unchanged
	eigenkills['kill_escore'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix, k=1)[1]))
	print_full(eigenkills.sort_values(by='kill_escore', ascending=False))

	print("Champion Kill Rank by eigenvector centralities normalized by kill counts:")
	eigenkills_norm = pd.DataFrame()
	eigenkills_norm['champion'] = pd.Series(champion_kill_dataframe.index)
	eigenkills_norm['kill_escore_norm'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix_norm, k=1)[1])) # eigenvector with largest eigenvalue (k=1); scipy >= 0.17.0
	print_full(eigenkills_norm.sort_values(by='kill_escore_norm', ascending=False))

	print("Champion Death Rank by eigenvector centralities without normalization:")
	eigendeaths = pd.DataFrame()
	eigendeaths['champion'] = pd.Series(champion_kill_dataframe.index)
	eigendeaths['death_escore'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix.transpose(), k=1)[1]))
	print_full(eigendeaths.sort_values(by='death_escore', ascending=False))

	print("Champion Rank Kill/Death by eigenvector centralities")
	eigenranks = pd.DataFrame()
	eigenranks['champion'] = pd.Series(champion_kill_dataframe.index)
	eigenranks['kill_escore'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix, k=1)[1]))
	eigenranks['death_escore'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix.transpose(), k=1)[1]))
	eigenranks['eranks'] = eigenranks['kill_escore'] / eigenranks['death_escore']
	print_full(eigenranks.sort_values(by='eranks', ascending=False))	

	print("Champion Rank Kill-Death by eigenvector centralities")
	eigenranks = pd.DataFrame()
	eigenranks['champion'] = pd.Series(champion_kill_dataframe.index)
	eigenranks['kill_escore'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix, k=1)[1]))
	eigenranks['death_escore'] = pd.DataFrame(abs(linalg.eigs(champion_kill_matrix.transpose(), k=1)[1]))
	eigenranks['eranks'] = eigenranks['kill_escore'] - eigenranks['death_escore']
	print_full(eigenranks.sort_values(by='eranks', ascending=False))	

	# PageRank: similar result with eigenvector centrality

	G = nx.to_networkx_graph(champion_kill_matrix)
	G_transpose = nx.to_networkx_graph(champion_kill_matrix.transpose())

	pr = nx.pagerank(G)
	prkills = pd.DataFrame()
	prkills['champion'] = pd.Series(champion_kill_dataframe.index)
	prkills['kill_prscore'] = pd.DataFrame(data=list(pr.values()), index=list(pr.keys()))
	print_full(prkills.sort_values(by='kill_prscore', ascending=False))	

	pr_t = nx.pagerank(G_transpose)
	prdeaths = pd.DataFrame()
	prdeaths['champion'] = pd.Series(champion_kill_dataframe.index)
	prdeaths['death_prscore'] = pd.DataFrame(data=list(pr_t.values()), index=list(pr_t.keys()))
	print_full(prdeaths.sort_values(by='death_prscore', ascending=False))	

	# HITS: hub=auth

	hub, auth = nx.hits(G)
	hitskills = pd.DataFrame()
	hitskills['champion'] = pd.Series(champion_kill_dataframe.index)
	hitskills['kill_hitsscore'] = pd.DataFrame(data=list(hub.values()), index=list(hub.keys()))
	print_full(hitskills.sort_values(by='kill_hitsscore', ascending=False))	
	hitsdeaths = pd.DataFrame()
	hitsdeaths['champion'] = pd.Series(champion_kill_dataframe.index)
	hitsdeaths['death_hitsscore'] = pd.DataFrame(data=list(auth.values()), index=list(auth.keys()))
	print_full(hitsdeaths.sort_values(by='death_hitsscore', ascending=False))	

def champion_assist_rank(champion_assist_dataframe):

	champion_assist_matrix = champion_assist_dataframe.as_matrix()
	row_sum = champion_assist_matrix.sum(axis=1)
	champion_assist_matrix_norm = champion_assist_matrix / row_sum[:, numpy.newaxis] # broadcast

	print("Champion assist Rank by counts:")
	countassists = pd.DataFrame()
	countassists['champion'] = pd.Series(champion_assist_dataframe.index)
	countassists['assist_count'] = champion_assist_matrix.sum(axis=1)
	print_full(countassists.sort_values(by='assist_count', ascending=False))

	print("Champion assist Rank by eigenvector centralities without normalization:")
	eigenassists = pd.DataFrame()
	eigenassists['champion'] = pd.Series(champion_assist_dataframe.index)
	eigenassists['assist_escore'] = pd.DataFrame(abs(linalg.eigs(champion_assist_matrix, k=1)[1]))
	print_full(eigenassists.sort_values(by='assist_escore', ascending=False))

	print("Champion assist Rank by eigenvector centralities normalized by assist counts:")
	eigenassists_norm = pd.DataFrame()
	eigenassists_norm['champion'] = pd.Series(champion_assist_dataframe.index)
	eigenassists_norm['assist_escore_norm'] = pd.DataFrame(abs(linalg.eigs(champion_assist_matrix_norm, k=1)[1])) # eigenvector with largest eigenvalue (k=1); scipy >= 0.17.0
	print_full(eigenassists_norm.sort_values(by='assist_escore_norm', ascending=False))

if __name__ == '__main__':
	main()