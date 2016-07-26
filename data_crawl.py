# -*- coding: utf-8 -*-
"""
LoLa data crawling based on Cassiopeia.
"""

from cassiopeia import riotapi
from cassiopeia import type
from cassiopeia.type.api.exception import APIError
import sqlite3
import pandas as pd
import math
import time 
import random

def auto_retry(api_call_method):
    """ A decorator to automatically retry 500/503s (Service Unavailable) and skip 400s (Bad Request) or 404 (Not Found). """
    def call_wrapper(*args, **kwargs):
        try:
            return api_call_method(*args, **kwargs)
        except APIError as error:
            # try again once
            if error.error_code in [500, 503]:
                try:
                    print("Got a 500 or 503, trying again after 5 seconds...")
                    time.sleep(5)
                    return api_call_method(*args, **kwargs)
                except APIError as another_error:
                    if another_error.error_code in [500, 503, 400, 404]:
                        pass
                    else:
                        raise another_error

            # skip
            elif error.error_code in [400, 404]:
                print("Got a 400 or 404")
                pass # may make match None in auto_retry(riotapi.get_match)!

            # fatal
            else:
                raise error
    return call_wrapper


def riotapi_setting(api_key, region):
    try:
        riotapi.set_rate_limits((10, 10), (500, 600))
        riotapi.set_api_key(api_key)
        riotapi.set_region(region)
    except Exception as e:
        raise e

def main():
    riotapi.get_summoner_by_id = auto_retry(riotapi.get_summoner_by_id) # handling server errors
    riotapi.get_match_list = auto_retry(riotapi.get_match_list)
    riotapi.get_match = auto_retry(riotapi.get_match)

    print('\nCrawling process starts...')

    # set your api_key, region, seed_summoner_id, seasons, ranked_queues
    # inadequate settings of may lead to 404
    riotapi_setting(api_key, region='NA')
    begin_crawling(seed_summoner_id='22005573', seasons='PRESEASON2016',ranked_queues='RANKED_SOLO_5x5')

def begin_crawling(seed_summoner_id, seasons, ranked_queues):
    '''
    Breadth first crawling interations, Summoner -> Match -> Summoner...
    '''
    #seed intialization
    try:
        print('Seed initializing...')
        seed_summoner = riotapi.get_summoner_by_id(seed_summoner_id)    
        conn = sqlite3.connect('lola.db')
        conn.execute("INSERT INTO Summoner VALUES('{}','{}',{})".format(seed_summoner.id, seed_summoner.name, 0)) #watch out "" / ''
        conn.commit()
        conn.close()
        print('\nInitialization completed.')
    except Exception as e:
        print('\nInitialization failed: ', e) # possibly because the seed is already in database
        pass
 
    # summoner queue interations
    total_summoner_processed = 0           
    total_match_processed = 0
    total_match_cralwed = 0
    total_match_duplicate = 0
    total_match_none = 0
    iteration = 0
    try:
        conn = sqlite3.connect('lola.db')
        queue_summoner_ids = pd.read_sql("SELECT summoner_id FROM Summoner WHERE is_crawled=0", conn)
    except Exception as e:
        raise(e)
    finally:
        conn.close()
    while not queue_summoner_ids.empty:
        print('\nSummoner Queue Length:', len(queue_summoner_ids))
        iteration += 1 # only a relative number because of crawling restrarts 
        print ('Iteration', iteration, 'in the process...')
        queue_summoner_ids_list = list(queue_summoner_ids['summoner_id'])
        random.shuffle(queue_summoner_ids_list)
        for summoner_id in queue_summoner_ids_list[:]: # pd.dataframe to list of list(queue_summoner_ids['summoner_id'])
            conn = sqlite3.connect('lola.db')
            summoner = riotapi.get_summoner_by_id(summoner_id)
            match_reference_list = riotapi.get_match_list(summoner=summoner, seasons=seasons, ranked_queues=ranked_queues)

            if match_reference_list is None: # TODO: tag this summoner to be 400/404 status (or the loop may happen quite rarely)
                print("Summoner {} has None MatchList, skip..".format(summoner_id))
                continue

            print('\nSummoner {} ({}) in {}, {}: '.format(summoner.name, summoner.id, ranked_queues, seasons))
            print('Total Match Number of the summoner: {}'.format(len(match_reference_list)))

            match_no = 0 # crawled + duplicate + none
            crawled_match_no = 0
            duplicate_match_no = 0
            none_match_no = 0
            for  mf in match_reference_list[:]:
                if is_match_duplicate(mf, conn) == False:                    
                    try:
                        # TODO: urllib.error.URLError: <urlopen error [Errno 11001] getaddrinfo failed>
                        match = riotapi.get_match(mf) # match reference -> match
                    except Exception as e:
                        raise(e)
                    # may be None even if mf is not None, see https://github.com/meraki-analytics/cassiopeia/issues/57 
                    # can not use != because of Match.__eq__ use Match.id 
                    if match is None: 
                        none_match_no += 1
                        continue # jump to the next interation
                    match_to_sqlite(match, summoner, conn)
                    # match is crawled
                    conn.execute("UPDATE Match SET is_crawled = 1 WHERE match_id='{}'".format(mf.id))
                    crawled_match_no += 1
                else :
                    duplicate_match_no += 1
                match_no += 1
                if match_no % 10 == 0:                
                    print (match_no, 'matches in', len(match_reference_list), 'processed.')
            # summoner has been crawled
            conn.execute("UPDATE Summoner SET is_crawled = 1 WHERE summoner_id='{}'".format(summoner_id))
            conn.commit() # commit after every summoner finished
            conn.close()
            # sums of different kinds of matches
            total_summoner_processed += 1            
            total_match_processed += match_no
            total_match_cralwed += crawled_match_no
            total_match_duplicate += duplicate_match_no
            total_match_none += none_match_no
            print('\ntotal processed summoner:', total_summoner_processed,'\ntotal processed match:', total_match_processed, \
                  '\ntotal crawled match', total_match_cralwed, '\ntotal duplicate match:', total_match_duplicate,  \
                  '\ntotal none match:', total_match_none)

        # read new queue for next iteration
        try:
            conn = sqlite3.connect('lola.db')
            queue_summoner_ids = pd.read_sql("SELECT summoner_id FROM Summoner WHERE is_crawled=0", conn) #update queue
        except Exception as e:
            raise(e)
        finally:
            conn.close()

def is_match_duplicate(match_reference, conn):
    '''
    Check if a given match has a record in database
    '''
    try:
        is_empty = pd.read_sql("SELECT * FROM Match WHERE match_id = '{}'".format(match_reference.id), conn).empty
    except Exception as e:
        conn.close()
        raise(e)
        
    return not is_empty

def match_to_sqlite(match, summoner, conn):
    '''
    Store Match basic information to database;
    Arrange extraction and storation of match detail information
    '''
    #match basic
    match_id = match.id
    version = match.version
    duration = math.ceil((match.duration).total_seconds() / 60) #minute
    #data = str(match.data) # discarded
    try:
        conn.execute("INSERT INTO Match VALUES(?,?,?,?,?,?)", (match_id, version, duration, None, 0, 0))
    except Exception as e:
        conn.close()
        raise(e)

    # match details
    team_to_sqlite(match.red_team, match, conn)
    team_to_sqlite(match.blue_team, match, conn)
    for p in match.participants[:]:
        summoner_to_sqlite(p, summoner, conn)
        participant_to_sqlite(p, match, conn)
        participant_timeline_to_sqlite(p, match, conn)

    if match.timeline is None: # match.timeline may be None
        print("Match {} does not have Match.Timeline data, skip..".format(match.id))
        return
    if match.timeline.frames is None: # match.timeline.frames may be None
        print("Match {} does not have Match.Timeline.Frames data, skip..".format(match.id))
        return

    for f in match.timeline.frames[:]:
        frame_kill_event_to_sqlite(f, match, conn)

def team_to_sqlite(team, match, conn):
    '''
    Extract Match.Team Information to database
    '''
    match_id = match.id
    team_side = str(team.side)[5:]
    team_dragon_kills = team.dragon_kills
    team_baron_kills = team.baron_kills
    team_win = int(team.win) # binary to int
    team_bans = team.bans
    try:
        conn.execute("INSERT INTO Team VALUES(?,?,?,?,?)", (match_id, team_side, team_dragon_kills, team_baron_kills, team_win))
        for b in team_bans:
            ban = str(b)[4:-1] # Cass to text
            conn.execute("INSERT INTO TeamBan VALUES(?,?,?)", (match_id, team_side, ban))
    except Exception as e:
        conn.close()
        raise(e)

def summoner_to_sqlite(participant, summoner, conn):
    '''
    Extract Summoner basic information to database. (duplicate handled in database)
    '''
    summoner_id = participant.summoner_id
    if summoner_id != summoner.id:
        summoner_name = participant.summoner_name
        is_crawled = 0
        try:
            #summoner_id is UNIQUE in database
            conn.execute("INSERT INTO Summoner VALUES(?,?,?)", (summoner_id, summoner_name, is_crawled))
        except Exception:
            #print(e, summoner_name)
            pass

def participant_to_sqlite(participant, match, conn):
    '''
    Extract Match.Participant Information to database
    '''
    #match initial
    summoner_id = participant.summoner_id
    match_id = match.id
    side = str(participant.side)[5:]
    participant_id = participant.id
    champion = participant.champion.name
    previous_season_tier = participant.previous_season_tier.value # bug fixed in Cass, see: https://github.com/meraki-analytics/cassiopeia/issues/55
    #masteries = participant.masteries # discarded
    #runes = participant.runes # discarded
    summoner_spell_d = str(participant.summoner_spell_d) # Cass to text
    summoner_spell_f = str(participant.summoner_spell_f) # Cass to text   

    # match stats
    participant_stats = participant.stats
    kda = participant_stats.kda
    kills = participant_stats.kills
    deaths = participant_stats.deaths
    assists = participant_stats.assists
    champion_level = participant_stats.champion_level
    turret_kills = participant_stats.turret_kills
    cs = participant_stats.cs # farming
    killing_sprees = participant_stats.killing_sprees
    largest_critical_strike = participant_stats.largest_critical_strike
    largest_killing_spree = participant_stats.largest_killing_spree
    largest_multi_kill = participant_stats.largest_multi_kill
    gold_earned = participant_stats.gold_earned
    gold_spent = participant_stats.gold_spent
    magic_damage_dealt = participant_stats.magic_damage_dealt
    magic_damage_dealt_to_champions = participant_stats.magic_damage_dealt_to_champions
    magic_damage_taken = participant_stats.magic_damage_taken
    physical_damage_dealt = participant_stats.physical_damage_dealt
    physical_damage_dealt_to_champions = participant_stats.physical_damage_dealt_to_champions
    physical_damage_taken = participant_stats.physical_damage_taken
    true_damage_dealt = participant_stats.true_damage_dealt # physical_damage_dealt + magic_damage_dealt + true_damage_dealt
    true_damage_dealt_to_champions = participant_stats.true_damage_dealt_to_champions
    true_damage_taken = participant_stats.true_damage_taken
    damage_dealt = participant_stats.damage_dealt
    damage_dealt_to_champions = participant_stats.damage_dealt_to_champions
    damage_taken = participant_stats.damage_taken
    healing_done = participant_stats.healing_done
    units_healed = participant_stats.units_healed
    crowd_control_dealt = participant_stats.crowd_control_dealt
    vision_wards_bought = participant_stats.vision_wards_bought
    ward_kills = participant_stats.ward_kills
    wards_placed = participant_stats.wards_placed
    participant_win = int(participant_stats.win)

    try:
        conn.execute("INSERT INTO Participant VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", \
            (summoner_id, match_id, participant_id, side, champion, previous_season_tier, summoner_spell_d, summoner_spell_f, \
             kda, kills, deaths, assists, champion_level, turret_kills, cs, killing_sprees, largest_critical_strike, largest_killing_spree, largest_multi_kill, \
             gold_earned, gold_spent, magic_damage_dealt, magic_damage_dealt_to_champions, magic_damage_taken, physical_damage_dealt, physical_damage_dealt_to_champions, physical_damage_taken, \
             true_damage_dealt, true_damage_dealt_to_champions, true_damage_taken, damage_dealt, damage_dealt_to_champions, damage_taken, healing_done, units_healed, \
             crowd_control_dealt, vision_wards_bought, ward_kills, wards_placed, participant_win) )
    except sqlite3.Error as e:
        conn.close()
        raise(e)    

def participant_timeline_to_sqlite(participant, match, conn):
    '''
    Extract Match.Participant.Timeline information to database
    '''
    summoner_id = participant.summoner_id
    match_id = match.id
    side = str(participant.side)[5:]
    participant_id = participant.id

    participant_timeline = participant.timeline
    role = participant_timeline.role.value
    lane = participant_timeline.lane.value
    creeps_per_min_deltas = participant_timeline.creeps_per_min_deltas
    cs_diff_per_min_deltas = participant_timeline.cs_diff_per_min_deltas
    gold_per_min_deltas = participant_timeline.gold_per_min_deltas
    xp_per_min_deltas = participant_timeline.xp_per_min_deltas
    xp_diff_per_min_deltas = participant_timeline.xp_diff_per_min_deltas
    damage_taken_per_min_deltas = participant_timeline.damage_taken_per_min_deltas
    damage_taken_diff_per_min_deltas = participant_timeline.damage_taken_diff_per_min_deltas

    try:
        deltas_tuple = (creeps_per_min_deltas, cs_diff_per_min_deltas, gold_per_min_deltas, xp_per_min_deltas, 
                        xp_diff_per_min_deltas, damage_taken_per_min_deltas, damage_taken_diff_per_min_deltas)
        zero_to_ten = [deltas.zero_to_ten if deltas else None for deltas in deltas_tuple]
        ten_to_twenty = [deltas.ten_to_twenty if deltas else None for deltas in deltas_tuple]
        twenty_to_thirty = [deltas.twenty_to_thirty if deltas else None for deltas in deltas_tuple]
        thirty_to_end = [deltas.thirty_to_end if deltas else None for deltas in deltas_tuple]

    except Exception as e:
            conn.close()
            raise(e)
            
    data_deltas = {'zero_to_ten': zero_to_ten, 'ten_to_twenty': ten_to_twenty, 'twenty_to_thirty': twenty_to_thirty, 'thirty_to_end': thirty_to_end}
    try:
        for delta, values in data_deltas.items():
            creeps_per_min_delta = values[0]
            cs_diff_per_min_delta = values[1]
            gold_per_min_delta = values[2]
            xp_per_min_delta = values[3]
            xp_diff_per_min_delta = values[4]
            damage_taken_per_min_delta = values[5]
            damage_taken_diff_per_min_delta = values[6]
            conn.execute("INSERT INTO ParticipantTimeline VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", \
                            (summoner_id, match_id, delta, side, participant_id, role, lane, \
                             creeps_per_min_delta, cs_diff_per_min_delta, gold_per_min_delta, xp_per_min_delta, \
                             xp_diff_per_min_delta, damage_taken_per_min_delta, damage_taken_diff_per_min_delta) )
    except Exception as e:
            conn.close()
            raise(e)

def frame_kill_event_to_sqlite(frame, match, conn):
    '''
    Extract Match.Timeline.Frame.Event information to database (only kill events between participants)
    '''
    match_id = match.id
    minute = frame.timestamp.seconds // 60
    events = frame.events
    try:
        for event in events[:]:
            if event.type == type.core.common.EventType.kill and event.killer and event.victim: # there exists victim without killer
                happen = event.timestamp.seconds
                killer = event.killer.champion.name
                victim = event.victim.champion.name
                assists = event.assists
                if len(assists) == 0:
                    conn.execute("INSERT INTO FrameKillEvent VALUES(?,?,?,?,?,?)", (match_id, happen, victim, minute, killer, None))
                else:
                    for a in event.assists:
                        assist = a.champion.name
                        conn.execute("INSERT INTO FrameKillEvent VALUES(?,?,?,?,?,?)", (match_id, happen, victim, minute, killer, assist))

    except Exception as e:
        conn.close()
        raise(e)

if __name__ == "__main__":
    main()