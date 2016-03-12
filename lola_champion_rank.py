# -*- coding: utf-8 -*-
"""
LoLa data crawling based on Cassiopeia.
"""
import pandas as pd
import scipy

def champion_kill_rank(champion_kill_dataframe):
	
	champion_kill_matrix = champion_kill_dataframe.as_matrix()

	print("Champion Kill Rank by eigenvector centralities without normalization:")
	eigenkills = pd.DataFrame()
	eigenkills['champion'] = pd.Series(champion_kill_dataframe.index)
	eigenkills['kill_evector'] = pd.Series(abs(scipy.sparse.linalg.eigs(champion_kill_matrix, k=1)[1])) # eigenvector with largest eigenvalue (k=1); scipy >= 0.17.0
	print(eigenkills.sort('kill_evector', ascending=False))

	print("Champion Kill Rank by counts:")
	countkills = pd.DataFrame(champion_kill_matrix.sum(1), columns=['champion', 'kill_count']
	print(countkills.sort('kill_count', ascending=False))

def champion_assist_rank(champion_assist_matrix):
	pass