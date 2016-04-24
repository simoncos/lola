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
def similar_champions(champion_name):
    kill_matrix = champion_matrix.sqlite_to_kill_matrix('picks') # norm by picks
    kill_matrix_T = kill_matrix.T
    coci_kill_matrix = kill_matrix * kill_matrix_T # coci_kill
    temp_coci_kill_ten = pd.DataFrame(coci_kill_matrix.ix[champion_name]).sort(champion_name,ascending=False).iloc[0:10]

    plt_coci_kill = temp_coci_kill_ten.plot(kind='barh', title=champion_name + ' is similar with(TOP 10)', stacked=False).set_xlabel('Proportion').get_figure()
    plt_coci_kill.savefig(champion_name + '_similar.png')

#-----assist matrix-----#
def good_partner(champion_name):
    assist_matrix = champion_matrix.sqlite_to_assist_matrix('picks') # norm by picks
    assist_matrix_T = assist_matrix.T 
    coci_matrix = assist_matrix * assist_matrix_T # coci_assist
    temp_coci_ten = pd.DataFrame(coci_matrix.ix[champion_name]).sort(champion_name,ascending=False).iloc[0:10]

    plt_coci = temp_coci_ten.plot(kind='barh', title='Good partner of ' + champion_name + '(TOP 10)', stacked=False).set_xlabel('Proportion').get_figure()
    plt_coci.savefig(champion_name + '_similar.png')


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