# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 18:08:20 2016

@author: lzsim
"""

from cassiopeia import riotapi
from cassiopeia import core
from cassiopeia import type

import math

''' Classes Hierarchy, Reference: https://github.com/robrua/cassiopeia/tree/master/cassiopeia/type/
- Summoner core.summonerapi.get_summoner_by_id(summoner_id) 
- MatchList core.matchlistapi.get_match_list(Summoner, ...)
	- MatchReference
- MatchDetail core.matchapi.get_match(MatchReference)
  - Participants [Participant]
    - ParticipantStats
    - Timeline
  - Timeline
    - Frames [Frame]
      - Events [Event]
  - Team
'''

riotapi.set_region("NA")
riotapi.set_api_key("04c9abf6-0c85-406c-8520-3d86684e9cb1")

summoner_id='22005573'
seasons = 'PRESEASON2016'
ranked_queues = 'RANKED_SOLO_5x5'
summoner = core.summonerapi.get_summoner_by_id(summoner_id)    

#match
match_list = core.matchlistapi.get_match_list(summoner=summoner, seasons=seasons, ranked_queues=ranked_queues)
match_reference = match_list[0]
match = core.matchapi.get_match(match_reference)
match_reference_1 = match_list[1]
match_1 = core.matchapi.get_match(match_reference_1)
version = match.version
duration = math.ceil((match.duration).total_seconds() / 60) #minute
data = match.data
#team
team = match.red_team
team_participant = team[0]
team_bans = team.bans
team_win = team.win
team_dragon_kills = team.dragon_kills
team_baron_kills = team.baron_kills
team_side = str(team.side)[5:]

#participant
participants = match.participants
participant = participants[0]
paticipant_id = participant.id
participant_summoner_id = participant.summoner_id
participant_champion = participant.champion.name
participant_previous_season_tier = participant.previous_season_tier.value
participant_masteries = participant.masteries #discarded
participant_runes = participant.runes #discarded
participant_summoner_spell_d = str(participant.summoner_spell_d)
participant_summoner_spell_f = str(participant.summoner_spell_f)

#paticipant.stats
participant_stats = participant.stats
kda = participant_stats.kda
kills = participant_stats.assists
deaths = participant_stats.deaths
assists = participant_stats.assists
champion_level = participant_stats.assists
turret_kills = participant_stats.turret_kills
cs = participant_stats.cs #minion + monster kills
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
true_damage_dealt = participant_stats.true_damage_dealt #physical_damage_dealt + magic_damage_dealt + true_damage_dealt == damage_dealt
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

#participant.timeline
participant_timeline = participant.timeline
role = participant_timeline.role #type/core/common.py
lane = participant_timeline.lane #type/core/common.py
creeps_per_min_deltas = participant_timeline.creeps_per_min_deltas
cs_diff_per_min_deltas = participant_timeline.cs_diff_per_min_deltas
gold_per_min_deltas = participant_timeline.gold_per_min_deltas
xp_diff_per_min_deltas = participant_timeline.xp_diff_per_min_deltas
damage_taken_diff_per_min_deltas = participant_timeline.damage_taken_diff_per_min_deltas
damage_taken_per_min_deltas = participant_timeline.damage_taken_per_min_deltas


zero_to_ten = (creeps_per_min_deltas.zero_to_ten, cs_diff_per_min_deltas.zero_to_ten, gold_per_min_deltas.zero_to_ten, xp_diff_per_min_deltas.zero_to_ten, damage_taken_diff_per_min_deltas.zero_to_ten, damage_taken_per_min_deltas.zero_to_ten)
ten_to_twenty = (creeps_per_min_deltas.ten_to_twenty, cs_diff_per_min_deltas.ten_to_twenty, gold_per_min_deltas.ten_to_twenty, xp_diff_per_min_deltas.ten_to_twenty, damage_taken_diff_per_min_deltas.ten_to_twenty, damage_taken_per_min_deltas.ten_to_twenty)
twenty_to_thirty = (creeps_per_min_deltas.twenty_to_thirty, cs_diff_per_min_deltas.twenty_to_thirty, gold_per_min_deltas.twenty_to_thirty, xp_diff_per_min_deltas.twenty_to_thirty, damage_taken_diff_per_min_deltas.twenty_to_thirty, damage_taken_per_min_deltas.twenty_to_thirty)
thirty_to_end = (creeps_per_min_deltas.thirty_to_end, cs_diff_per_min_deltas.thirty_to_end, gold_per_min_deltas.thirty_to_end, xp_diff_per_min_deltas.thirty_to_end, damage_taken_diff_per_min_deltas.thirty_to_end, damage_taken_per_min_deltas.thirty_to_end)
data_deltas = {'zero_to_ten': zero_to_ten, 'ten_to_twenty': ten_to_twenty, 'twenty_to_thirty': twenty_to_thirty, 'thirty_to_end': thirty_to_end}
for dd in data_deltas:
    creeps_per_min_delta = data_deltas[dd][0]
    cs_diff_per_min_delta = data_deltas[dd][1]
    gold_per_min_delta = data_deltas[dd][2]
    xp_diff_per_min_delta = data_deltas[dd][3]
    damage_taken_diff_per_min_delta = data_deltas[dd][4]
    damage_taken_per_min_delta = data_deltas[dd][5]
    print (dd, creeps_per_min_delta, cs_diff_per_min_delta, gold_per_min_delta, xp_diff_per_min_delta, damage_taken_diff_per_min_delta, damage_taken_per_min_delta)

#match.timeline.frames
frames = match.timeline.frames
frame = frames[20]
events = frame.events
event = events[0]
event_type = event.type #type/core/common.py
event_assist = event.assists[0].champion.name
minute = frame.timestamp.seconds // 60
happen = event.timestamp.seconds
frames_1 = match_1.timeline.frames
frame_1 = frames_1[12]

for event in frames[15].events[:]:
    if event.type == type.core.common.EventType.kill and event.killer and event.victim: # there exists victim without killer
        print (event, event.assists, len(event.assists))