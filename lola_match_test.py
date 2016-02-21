# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 21:56:17 2016

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