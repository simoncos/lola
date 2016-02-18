# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 13:55:24 2016

@author: Che
"""

from cassiopeia import riotapi
from cassiopeia import core
from cassiopeia import type
import pandas as pd

riotapi.set_region("NA")
riotapi.set_api_key("04c9abf6-0c85-406c-8520-3d86684e9cb1")

def demo_kill_event(summoner_id='22005573'):#name = 'caaaaaaaaaaaaake'

    seasons = 'PRESEASON2016'
    ranked_queues = 'RANKED_SOLO_5x5'
    summoner = core.summonerapi.get_summoner_by_id(summoner_id)    
    match_list = core.matchlistapi.get_match_list(summoner=summoner, seasons=seasons, ranked_queues=ranked_queues)
    
    print('Summoner {0} in {1} {2}: '.format(summoner_id, seasons, ranked_queues))
    print('Total Matches Number: {0}'.format(len(match_list)))

    match_id_list = []
    summoner_id_list = []
    kill_event_list = []
    for m in match_list[:]:#m is MatchReference
        try:
            match = core.matchapi.get_match(m)
        except Exception as e:
            print ('\nError: {0}', e)
            continue
        # if exist match_id in MatchTeam (means duplicate), break)        
        match_id_list.append(m.id)#match_id
        participants = match.participants            
        for p in participants[:]:
            summoner_id_list.append(p.summoner_id)
        frames = match.timeline.frames
        for f in frames[:]:
            events = f.events
            for e in events[:]:
                if e.type == type.core.common.EventType.kill and e.killer and e.victim:
                    kill_event_list.append([e.killer.champion, e.victim.champion])
    
    df_match_ids = pd.DataFrame(data = list(set(match_id_list)), columns=['match_id']) #set
    with open('lola_match.csv','a+') as mf:    
        df_match_ids.to_csv(mf, sep='\t', index=False)

    df_summoner_ids = pd.DataFrame(data = list(set(summoner_id_list)), columns=['summoner_id']) #set
    with open('lola_summoner.csv','a+') as sf:    
        df_summoner_ids.to_csv(sf, sep='\t', index=False)    

    df_kill_event = pd.DataFrame(data = kill_event_list, columns=['killer_champion', 'victim_champion'])
    with open('lola_kill_event.csv','a+') as sf:    
        df_kill_event.to_csv(sf, sep='\t', index=False)   


