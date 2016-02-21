# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:37:50 2016

@author: lzsim
"""

from cassiopeia import riotapi
from cassiopeia import core
from cassiopeia import type
import sqlite3
import pandas as pd

seed_summoner_id='22005573'

conn = sqlite3.connect('lola_test.db')

try:
    #len(pd.read_sql("SELECT * from Summoner", conn)) == 0:
    #seed_summoner = core.summonerapi.get_summoner_by_id(seed_summoner_id)    
    #conn.execute("INSERT INTO Summoner VALUES('{}','{}',{})".format(seed_summoner.id, seed_summoner.name, 0))
    #conn.execute("INSERT INTO Team VALUES('{}','{}','{}',{},{},{})".format('1','1', 'aa', 2, 3, 1))
    #queue_summoner_ids = pd.read_sql("SELECT summoner_id FROM Summoner WHERE is_crawled=0", conn)
    conn.execute("INSERT INTO ParticipantTimeline VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (1,1,1,1,1,1,1,None,None, None, None, None,None,1))
    conn.commit()
    conn.close()
except Exception as e:
    raise e