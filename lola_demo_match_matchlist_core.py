#import random
from cassiopeia import riotapi
from cassiopeia import core
from cassiopeia import type

riotapi.set_region("NA")
riotapi.set_api_key("04c9abf6-0c85-406c-8520-3d86684e9cb1")

def ChampionKill():

    summoner_name = 'caaaaaaaaaaaaake'
    summoner = core.summonerapi.get_summoner_by_name(summoner_name)
    seasons = 'PRESEASON2016'
    ranked_queues = 'RANKED_SOLO_5x5'
    
    ml = core.matchlistapi.get_match_list(summoner=summoner, seasons=seasons, ranked_queues=ranked_queues)
    
    print 'Summoner', summoner_name, 'in', seasons, ranked_queues, ':'
    print 'Total Matches Number:', len(ml)
    
    for m in ml[:1]:
        print '\nMatch', m.id #m is MatchReference
        match = core.matchapi.get_match(m)
        participants = match.participants
        for p in participants:
            print p.summoner_id, p.id, p.champion
        frames = match.timeline.frames
        for f in frames[:7]:
            events = f.events
            print '\n\n', f
            print 'total events number:', len(events)
            for e in events[:]:
                if e.type == type.core.common.EventType.kill:
                    print '\nkiller:', e.killer, 'victim:', e.victim
                    print 'assist:'
                    if e.assists == []:
                        print 'No Assists'
                    else:
                        for a in e.assists:
                            print a
                   
                #print '\nJson Data:', e.data 

def ChampionList():
    champions = riotapi.get_champions()
    print 'Total Champion Number:', len(champions)
    for c in champions:
        print c.id, c.name

def ChampionList_test():
    i = 1
    h = 0
    while (h < 129):
        i += 1
        try:
            champion_name = riotapi.get_champion_by_id(i).name
            h += 1
            print '{}\t{}\t{}'.format(i, champion_name, h)
        except:
            print '{}\t{}\t{}'.format(i, None, None)

#pd.DataFram1e(data=[[1,2],[3,4]])