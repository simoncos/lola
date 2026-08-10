# -*- coding: utf-8 -*-
"""
LoLa champion relationship
"""
import champion_matrix as lola


def bibliographic_coupling(adjacency):
    """Return row-profile coupling B = A A^T with labels preserved."""
    return adjacency.dot(adjacency.T)


def top_counter_scores(kill_matrix, champion_name, limit=10):
    """Return killers of champion_name from a killer-by-victim matrix."""
    return (
        kill_matrix[champion_name]
        .drop(labels=[champion_name], errors='ignore')
        .sort_values(ascending=False)
        .iloc[0:limit]
    )

#-----kill matrix-----#
def similar_killer(champion_name):
    kill_matrix_adjacency = lola.sqlite_to_kill_matrix('picks').T # norm by picks; edge from column to row
    bibli_kill_matrix = bibliographic_coupling(kill_matrix_adjacency)
    temp_bibli_kill_ten = (
        bibli_kill_matrix.loc[champion_name]
        .drop(labels=[champion_name], errors='ignore')
        .sort_values(ascending=False)
        .iloc[0:10]
    )

    plt_bibli_kill = temp_bibli_kill_ten.plot(kind='barh', title=champion_name + ' is similar with(TOP 10)', stacked=False).set_xlabel('Proportion').get_figure()
    plt_bibli_kill.savefig(champion_name + '_similar_killer.png')

#-----assist matrix-----#
def good_partner(champion_name):
    assist_matrix_adjacency = lola.sqlite_to_assist_matrix('picks').T # norm by picks; edge from column to row
    bibli_matrix = bibliographic_coupling(assist_matrix_adjacency)
    temp_bibli_ten = (
        bibli_matrix.loc[champion_name]
        .drop(labels=[champion_name], errors='ignore')
        .sort_values(ascending=False)
        .iloc[0:10]
    )

    plt_bibli = temp_bibli_ten.plot(kind='barh', title='Good partner of ' + champion_name + '(TOP 10)', stacked=False).set_xlabel('Proportion').get_figure()
    plt_bibli.savefig(champion_name + '_partner.png')


#-----champion counter-----#
def counter(champion_name):
    kill_matrix = lola.sqlite_to_kill_matrix('picks') # norm by picks
    # Rows are killers and columns are victims, so the victim column lists
    # champions that killed the requested champion.
    temp_series = top_counter_scores(kill_matrix, champion_name)
    plttt = temp_series.plot(kind='barh', title='Top 10 choices to counter ' + champion_name, stacked=False).set_xlabel('Proportion').get_figure()
    plttt.savefig(champion_name +'_counter.png')
    

#-----champion assist-----#
def assist(champion_name):
    assist_matrix = lola.sqlite_to_assist_matrix('picks') # norm by picks
    temp_series = (
        assist_matrix[champion_name]
        .drop(labels=[champion_name], errors='ignore')
        .sort_values(ascending=False)
        .iloc[0:10]
    ) # select column, champion_name was assisted by row
    plttt = temp_series.plot(kind='barh', title='Top 10 choices to assist ' + champion_name, stacked=False).set_xlabel('Proportion').get_figure()
    plttt.savefig(champion_name + '_assist.png')
