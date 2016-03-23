ATTACH DATABASE 'lola_challenger.db' AS 'challenger';
ATTACH DATABASE 'lola_diamond.db' AS 'diamond';
ATTACH DATABASE 'lola_silver.db' AS 'silver';
ATTACH DATABASE 'lola_merged.db' AS 'merged';

INSERT OR IGNORE INTO 'merged'.Team SELECT * FROM (SELECT * FROM 'challenger'.Team 
																						UNION SELECT * FROM 'diamond'.Team 
																						UNION SELECT * FROM 'silver'.Team);
INSERT OR IGNORE INTO 'merged'.TeamBan SELECT * FROM (SELECT * FROM 'challenger'.TeamBan 
																						UNION SELECT * FROM 'diamond'.TeamBan 
																						UNION SELECT * FROM 'silver'.TeamBan);
INSERT OR IGNORE INTO 'merged'.Summoner SELECT * FROM (SELECT * FROM 'challenger'.Summoner 
																						UNION SELECT * FROM 'diamond'.Summoner 
																						UNION SELECT * FROM 'silver'.Summoner);
INSERT OR IGNORE INTO 'merged'.Participant SELECT * FROM (SELECT * FROM 'challenger'.Participant 
																						UNION SELECT * FROM 'diamond'.Participant 
																						UNION SELECT * FROM 'silver'.Participant);
INSERT OR IGNORE INTO 'merged'.ParticipantTimeline SELECT * FROM (SELECT * FROM 'challenger'.ParticipantTimeline 
																						UNION SELECT * FROM 'diamond'.ParticipantTimeline 
																						UNION SELECT * FROM 'silver'.ParticipantTimeline);
INSERT OR IGNORE INTO 'merged'.Match SELECT * FROM (SELECT * FROM 'challenger'.Match 
																						UNION SELECT * FROM 'diamond'.Match 
																						UNION SELECT * FROM 'silver'.Match);
INSERT OR IGNORE INTO 'merged'.FrameKillEvent SELECT * FROM (SELECT * FROM 'challenger'.FrameKillEvent 
																						UNION SELECT * FROM 'diamond'.FrameKillEvent 
																						UNION SELECT * FROM 'silver'.FrameKillEvent);
DETACH DATABASE 'challenger';
DETACH DATABASE 'diamond';
DETACH DATABASE 'silver';
DETACH DATABASE 'merged';


/* 
check duplicate matches: |A ∩ B ∩ C| + |(A ∩ B) ∪ (A ∩ C) ∪ (B ∩ C)|

proof:

|A∪B∪C| = (|A|+|B|+|C|) - |A∩B| - |B∩C| - |C∩A| + |A∩B∩C|
				 = (|A|+|B|+|C|) - |(A ∩ B) ∪ (A ∩ C) ∪ (B ∩ C)| - |A∩B∩C|
(|A∩B| + |B∩C| + |C∩A| - 2|A∩B∩C| = |(A ∩ B) ∪ (A ∩ C) ∪ (B ∩ C)|)
*/

/*

A ∩ B ∩ C

JOIN method:
select c.match_id, c.version from ('challenger'.Match c
							join 'diamond'.Match d on c.match_id=d.match_id
							join 'silver'.Match s on c.match_id=s.match_id);

INTERSECTION method:
select match_id, version from (
			select * from 'challenger'.Match 
		intersect 
			select * from 'diamond'.Match 
		intersect 
			select * from 'silver'.Match);
*/


/*

(A ∩ B) ∪ (A ∩ C) ∪ (B ∩ C)

select match_id from (
			select * from (select * from 'challenger'.Match intersect select * from 'diamond'.Match)
		union 
			select * from (select * from 'challenger'.Match intersect select * from 'silver'.Match)
		union
			select * from (select * from 'diamond'.Match intersect select * from 'silver'.Match)
);

*/

