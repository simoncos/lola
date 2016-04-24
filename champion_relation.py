# -*- coding: utf-8 -*-
"""
LoLa champion relationship
"""
import pandas as pd
import sqlite3
import champion_matrix

#-----fetch picks bans-----#
conn = sqlite3.connect('lola.db')
pick_ban_infor = pd.read_sql("SELECT champion,picks,bans FROM ChampionMatchStats", conn, index_col=['champion'])
pick_infor_matrix = pick_ban_infor['picks']
conn.close()

#-----kill matrix-----#
def similar_killer(champion_name):
    kill_matrix_adjacency = champion_matrix.sqlite_to_kill_matrix('picks').T # norm by picks; edge from column to row
    bibli_kill_matrix = kill_matrix_adjacency.T * kill_matrix_adjacency # bibliography kill matrix, bibli_kill
    temp_bibli_kill_ten = pd.DataFrame(bibli_kill_matrix.ix[champion_name]).sort(champion_name,ascending=False).iloc[0:10]

    plt_bibli_kill = temp_bibli_kill_ten.plot(kind='barh', title=champion_name + ' is similar with(TOP 10)', stacked=False).set_xlabel('Proportion').get_figure()
    plt_bibli_kill.savefig(champion_name + '_similar_killer.png')

#-----assist matrix-----#
def good_partner(champion_name):
    assist_matrix_adjacency = champion_matrix.sqlite_to_assist_matrix('picks').T # norm by picks; edge from column to row
    bibli_matrix = assist_matrix_adjacency.T * assist_matrix_adjacency # bibliography assist matrix, bibli_assist
    temp_bibli_ten = pd.DataFrame(bibli_matrix.ix[champion_name]).sort(champion_name,ascending=False).iloc[0:10]

    plt_bibli = temp_bibli_ten.plot(kind='barh', title='Good partner of ' + champion_name + '(TOP 10)', stacked=False).set_xlabel('Proportion').get_figure()
    plt_bibli.savefig(champion_name + '_partner.png')


#-----champion counter-----#
def counter(champion_name):
    kill_matrix = champion_matrix.sqlite_to_kill_matrix('picks') # norm by picks
    temp_series = pd.DataFrame(kill_matrix.ix[champion_name]).sort(champion_name,ascending=False).iloc[0:10]#, ascending=False
    plttt = temp_series.plot(kind='barh', title='Top 10 choices to counter ' + champion_name, stacked=False).set_xlabel('Proportion').get_figure()
    plttt.savefig(champion_name +'_counter.png')
    

#-----champion assist-----#
def assist(champion_name):
    assist_matrix = champion_matrix.sqlite_to_assist_matrix('picks') # norm by picks
    temp_series = pd.DataFrame(assist_matrix[champion_name]).sort(champion_name,ascending=False).iloc[0:10] # select column ,column been assisted by row
    plttt = temp_series.plot(kind='barh', title='Top 10 choices to assist ' + champion_name, stacked=False).set_xlabel('Proportion').get_figure()
    plttt.savefig(champion_name + '_assist.png')