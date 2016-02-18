# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 18:08:20 2016

@author: lzsim
"""

from cassiopeia import riotapi
from cassiopeia import core
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
version = match.version
duration = math.ceil((match.duration).total_seconds() / 60) #minute

#team
team = match.red_team
team_participant = team[0]
team_bans = team.bans
team_win = team.win
team_dragon_kills = team.dragon_kills
team_baron_kills = team.baron_kills
team_side = team.side

#participant
participants = match.participants
participant = participants[0]
paticipant_id = participant.id
participant_summoner_id = participant.summoner_id
participant_champion = participant.champion.name
participant_previous_season_tier = participant.previous_season_tier
participant_masteries = participant.masteries #discarded
participant_runes = participant.runes #discarded
participant_summoner_spell_d = participant.summoner_spell_d
participant_summoner_spell_f = participant.summoner_spell_f

#paticipant.stats
participant_stats = participant.stats
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
crowd_control_dealt = participant_stats.crowd_control_dealt
ward_kills = participant_stats.ward_kills
wards_placed = participant_stats.wards_placed
turret_kills = participant_stats.turret_kills
participant_win = participant.stats.win

#participant.timeline
participant_timeline = participant.timeline
participant_role = participant_timeline.role #type/core/common.py
participant_lane = participant_timeline.lane #type/core/common.py

participant_gold_per_min_deltas = participant_timeline.gold_per_min_deltas
participant_gold_per_min_deltas_1020 = participant_gold_per_min_deltas.ten_to_twenty #ten_to_twenty, thirty_to_end, twenty_to_thirty, zero_to_ten 

participant_xp_diff_per_min_deltas = participant_timeline.xp_diff_per_min_deltas
participant_xp_per_min_deltas = participant_timeline.xp_per_min_deltas
participant_damage_taken_diff_per_min_deltas = participant_timeline.damage_taken_diff_per_min_deltas
participant_damage_taken_per_min_deltas = participant_timeline.damage_taken_per_min_deltas

#match.timeline.frames
frames = match.timeline.frames
frame = frames[20]
events = frame.events
event = events[0]
event_type = event.type #type/core/common.py
