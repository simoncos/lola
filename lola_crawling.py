# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 13:55:24 2016

@author: Che
"""

#import random
from cassiopeia import riotapi
from cassiopeia import core
from cassiopeia import type
import sqlite3
import pandas as pd
        
def begin_crawling(api_key, seed_summoner_id, region='NA', seasons='PRESEASON2016', ranked_queues='RANKED_SOLO_5x5'):

    #seed intialization
    try:
        riotapi.set_api_key(api_key)
        riotapi.set_region(region)
        seed_summoner = core.summonerapi.get_summoner_by_id(seed_summoner_id)    
        conn = sqlite3.connect('lola.db')
        conn.execute("INSERT INTO Summoner VALUES('{}','{}',{})".format(seed_summoner.id, seed_summoner.name, 0)) #watch out "" | ''
        conn.commit()
        queue_summoner_ids = pd.read_sql("SELECT * FROM Summoner WHERE is_crawled=0", conn)
        conn.close()
    except Exception as e:
        print(e)
 
    #queue interations
    iteration = 0
    while not queue_summoner_ids.empty:
        conn = sqlite3.connect('lola.db')
        iteration += 1
        print (iteration)
        for summoner_id in queue_summoner_ids[:]: 
            try:
                summoner = core.summonerapi.get_summoner_by_id(summoner_id)
                match_list = core.matchlistapi.get_match_list(summoner=summoner, seasons=seasons, ranked_queues=ranked_queues)
                print('Summoner {0} in {1} {2}: '.format(summoner.name, seasons, ranked_queues))
                print('Total Matches Number: {0}'.format(len(match_list)))

                for  mf in match_list[:]:
                    if is_match_duplicate(mf) == False:                     
                        try:
                            match = core.matchapi.get_match(mf) #match reference -> match
                            match_to_sqlite(match)
                            match_details_to_sqlite(match)
                        except Exception as e:
                            print (e)
                            continue
            except Exception as e:
                print('summoner id {}: {}'.format(summoner_id, e))
                continue
        queue_summoner_ids = pd.read_sql("SELECT summoner_id FROM Summoner WHERE is_crawled=0", conn) #update queue
        conn.close()

def is_match_duplicate(match_reference):
    try:
        is_empty = pd.read_sql("SELECT * FROM Match WHERE match_id = '{}'".format(match_reference.id), conn).empty
    except Exception as e:
        print(e)
    return not is_empty

def match_to_sqlite(match):
    match_id = match.id
    version = match.version
    duration = math.ceil((match.duration).total_seconds() / 60) #minute
    is_crawled = 1
    try:
        conn.execute("INSERT INTO Match VALUES('{}','{}',{},{})".format(match_id, version, duration, is_crawled))
    except Exception as e:
        print(e)

def match_details_to_sqlite(match):
    team_to_sqlite(match.red_team, match)
    team_to_sqlite(match.blue_team, match)
    for p in match.participants[:]:
        summoner_to_sqlite(p)
        participant_to_sqlite(p, match)
        participant_timeline_to_sqlite(p, match)
    for f in match.timeline.frames[:]:
        frame_kill_event_to_sqlite(f, match)
    #todo

def team_to_sqlite(match):
    team_bans = team.bans #todo: Cass - text
    team_win = team.win #todo: True - 1
    team_dragon_kills = team.dragon_kills
    team_baron_kills = team.baron_kills
    team_side = team.side #todo: Cass - text
    try:
        conn.execute("".format())
    except Exception as e:
        print(e)
    #todo

def summoner_to_sqlite(participant):
    summoner_id = participant.summoner_id
    summoner_name = participant.summoner_name
    is_crawled = 0
    try:
        conn.execute("INSERT INTO Summoner VALUES('{}','{}',{})".format(summoner_id, summoner_name, is_crawled)) #summoner_id UNIQUE in database
    except Exception as e:
        print(e)

def participant_to_sqlite(participant, match):
    # handle duplicate in database

    #match initial
    paticipant_id = participant.id
    summoner_id = participant.summoner_id
    champion = participant.champion.name
    previous_season_tier = participant.previous_season_tier # cass - text
    #masteries = participant.masteries #discarded
    #runes = participant.runes #discarded
    summoner_spell_d = participant.summoner_spell_d # cass - text
    summoner_spell_f = participant.summoner_spell_f # cass - text   

    #match stats
    kda = participant_stats.kda
    kills = participant_stats.assists
    assists = participant_stats.assists
    deaths = participant_stats.deaths
    champion_level = participant_stats.assists
    gold_earned = participant_stats.gold_earned
    gold_spent = participant_stats.gold_spent
    magic_damage_dealt = participant_stats.magic_damage_dealt
    magic_damage_dealt_to_champions = participant_stats.magic_damage_dealt_to_champions
    magic_damage_taken = participant_stats.magic_damage_taken
    physical_damage_dealt = participant_stats.physical_damage_dealt
    physical_damage_dealt_to_champions = participant_stats.physical_damage_dealt_to_champions
    physical_damage_taken = participant_stats.physical_damage_taken
    true_damage_dealt = participant_stats.true_damage_dealt #physical_damage_dealt + magic_damage_dealt + true_damage_dealt == damage_dealt
    true_damage_dealt_to_champions = participant_stats.true_damage_dealt_to_champions
    true_damage_taken = participant_stats.true_damage_taken
    damage_dealt = participant_stats.damage_dealt
    damage_dealt_to_champions = participant_stats.damage_dealt_to_champions
    damage_taken = participant_stats.damage_taken
    healing_done = participant_stats.healing_done
    crowd_control_dealt = participant_stats.crowd_control_dealt #???
    ward_kills = participant_stats.ward_kills
    wards_placed = participant_stats.wards_placed
    turret_kills = participant_stats.turret_kills
    participant_win = participant.stats.win # False - 0

    # todo
    try:
        conn.execute("".format())
    except Exception as e:
        print(e)    

def participant_timeline_to_sqlite(participant, match):
    # handle duplicate in database

    #todo: deltas - delta

    #todo:

    for d in delta:
        delta_ = d
        try:
            conn.execute("".format())
        except Exception as e:
            print(e)

def frame_kill_event_to_sqlite(frame, match):
    #TBD: frame_number? timestamp?
    #todo: delta
    events = frame.events
    for e in events[:]:
        if e.type == type.core.common.EventType.kill and e.killer and e.victim:
            killer = e.killer.champion
            victim = e.victim.champion
            assists = ''
            for a in e.assists: #TBD: Table Assist
                assists = 
            kill_event_list.append([e.killer.champion, e.victim.champion])                
    #todo
    try:
        conn.execute("".format())
    except Exception as e:
        print(e)
def main():
    begin_crawling(api_key='04c9abf6-0c85-406c-8520-3d86684e9cb1', seed_summoner_id='22005573')

if __name__ == "__main__":
    main()