CREATE TABLE `Summoner` (
                -- `id` integer NOT NULL,
                `summoner_id`   text NOT NULL UNIQUE, /*key*/
                `summoner_name` text NOT NULL,
                `is_crawled`    integer NOT NULL
                -- PRIMARY KEY(id)
);
CREATE TABLE `ParticipantTimeline` (
                -- `id` integer NOT NULL,
                `summoner_id`   text NOT NULL, /*key*/
                `match_id`      text NOT NULL, /*key*/
                `delta` text NOT NULL, /*key*/
                `side`  text NOT NULL,
                `participant_id` text NOT NULL,
                `role` text NOT NULL,
                `lane` text NOT NULL,

                `creeps_per_min_delta` real,
                `cs_diff_per_min_delta` real,
                `gold_per_min_delta` real,
                `xp_per_min_delta` real,
                `xp_diff_per_min_delta` real,
                `damage_taken_per_min_delta` real,
                `damage_taken_diff_per_min_delta` real
                -- PRIMARY KEY(id)
);
CREATE TABLE `Match` (
                -- `id` integer NOT NULL,
                `match_id`      text NOT NULL UNIQUE, /*key*/
                `version` text NOT NULL,
                `duration` integer NOT NULL,
                -- `season` text NOT NULL,
                `data` text,
                `is_crawled`    integer NOT NULL,
                `is_counted` integer NOT NULL /*for ChampionMatchStats*/
                -- PRIMARY KEY(id)
);
CREATE TABLE `MatchChampion` (
                `match_id`      integer NOT NULL, /*key*/
                `participant1`  text,
                `participant2`  text,
                `participant3`  text,
                `participant4`  text,
                `participant5`  text,
                `participant6`  text,
                `participant7`  text,
                `participant8`  text,
                `participant9`  text,
                `participant10` text
);
CREATE TABLE `FrameKillEvent` (
                -- `id` integer NOT NULL,
                `match_id`      text NOT NULL, /*key*/
                `happen`        integer NOT NULL, /*key*/
                `victim` text NOT NULL, /*key*/
                `minute`        integer NOT NULL,
                `killer` text NOT NULL,
                `assist` text
                -- PRIMARY KEY(id)
);
CREATE TABLE `Team` (
                -- `id` integer NOT NULL,
                `match_id`      text NOT NULL, /*key*/
                `side`  text NOT NULL, /*key*/
                `dragon_kills` integer NOT NULL,
                `baron_kills` integer NOT NULL,
                `win`   integer NOT NULL
                -- PRIMARY KEY(id)
);
CREATE TABLE `TeamBan` (
                -- `id` integer NOT NULL,
                `match_id`      text NOT NULL, /*key*/
                `side`  text NOT NULL, /*key*/
                `ban` text NOT NULL /*key*/
                -- PRIMARY KEY(id)
);
CREATE TABLE `Participant` (
                -- `id` integer NOT NULL,
                `summoner_id`   text NOT NULL, /*key*/
                `match_id`      text NOT NULL, /*key*/
                `participant_id` text NOT NULL, 
                `side`  text NOT NULL,
                `champion`      text NOT NULL,
                `previous_season_tier`  text,
                `summoner_spell_d` text NOT NULL,
                `summoner_spell_f` text NOT NULL,

                `kda` real NOT NULL,
                `kills` integer NOT NULL,
                `deaths` integer NOT NULL,
                `assists` integer NOT NULL,
                `champion_level` integer NOT NULL,
                `turret_kills` integer NOT NULL,
                `cs` integer NOT NULL, /*minion + monster kills*/
                `killing_sprees` integer NOT NULL,
                `largest_critical_strike` integer NOT NULL,
                `largest_killing_spree` integer NOT NULL,
                `largest_multi_kill` integer NOT NULL,
                `gold_earned` integer NOT NULL,
                `gold_spent` integer NOT NULL,
                `magic_damage_dealt` integer NOT NULL,
                `magic_damage_dealt_to_champions` integer NOT NULL,
                `magic_damage_taken` integer NOT NULL,
                `physical_damage_dealt` integer NOT NULL,
                `physical_damage_dealt_to_champions` integer NOT NULL,
                `physical_damage_taken` integer NOT NULL,
                `true_damage_dealt` integer NOT NULL,
                `true_damage_dealt_to_champions` integer NOT NULL,
                `true_damage_taken` integer NOT NULL,
                `damage_dealt` integer NOT NULL,
                `damage_dealt_to_champions` integer NOT NULL,
                `damage_taken` integer NOT NULL,
                `healing_done` integer NOT NULL,
                `units_healed` integer NOT NULL,
                `crowd_control_dealt` integer NOT NULL,
                `vision_wards_bought` integer NOT NULL,
                `ward_kills` integer NOT NULL,
                `wards_placed` integer NOT NULL,
                `participant_win` integer NOT NULL,
                CONSTRAINT unq_match_participant UNIQUE(match_id, participant_id)
                -- PRIMARY KEY(id)
);
CREATE TABLE `ChampionMatchStats` (
                `champion`      TEXT NOT NULL UNIQUE, /*key*/
                `picks` integer NOT NULL DEFAULT 0,
                `bans`  integer NOT NULL DEFAULT 0,                
                `wins`  integer NOT NULL DEFAULT 0,                             
                `kills` integer NOT NULL DEFAULT 0,
                `deaths`        integer NOT NULL DEFAULT 0,
                `assists`       integer NOT NULL DEFAULT 0,
                `gold_earned`   integer NOT NULL DEFAULT 0,
                `magic_damage`  integer NOT NULL DEFAULT 0,
                `physical_damage`       integer NOT NULL DEFAULT 0,
                `true_damage`   integer NOT NULL DEFAULT 0,
                `damage_taken`  integer NOT NULL DEFAULT 0,
                `crowd_control_dealt`   integer NOT NULL DEFAULT 0,
                `ward_kills`    integer NOT NULL DEFAULT 0,
                `wards_placed`  integer NOT NULL DEFAULT 0,
                `team_kills`   integer NOT NULL DEFAULT 0,
                `team_deaths`  integer NOT NULL DEFAULT 0,
                `team_assists` integer NOT NULL DEFAULT 0,
                `team_gold_earned`     integer NOT NULL DEFAULT 0,
                `team_magic_damage`    integer NOT NULL DEFAULT 0,
                `team_physical_damage` integer NOT NULL DEFAULT 0,
                `team_true_damage`     integer NOT NULL DEFAULT 0,
                `team_damage_taken`    integer NOT NULL DEFAULT 0,
                `team_crowd_control_dealt`     integer NOT NULL DEFAULT 0,
                `team_ward_kills`      integer NOT NULL DEFAULT 0,
                `team_wards_placed`    integer NOT NULL DEFAULT 0,
                `label` integer DEFAULT 0,
                `version` text,
                `avg_tier` text
);
CREATE TABLE `ChampionRank` (
                `champion`      text NOT NULL UNIQUE, /*key*/
                `pick_rate`  real NOT NULL DEFAULT 0,                
                `ban_rate`  real NOT NULL DEFAULT 0,                
                `win_rate`  real NOT NULL DEFAULT 0,
                `kill_rate` real NOT NULL DEFAULT 0,
                `assist_rate` real NOT NULL DEFAULT 0,
                `death_rate` real NOT NULL DEFAULT 0,
                `eigen` real NOT NULL DEFAULT 0,
                `eigen_ratio` real NOT NULL DEFAULT 0,
                `eigen_diff` real NOT NULL DEFAULT 0,
                `pagerank` real NOT NULL DEFAULT 0,
                `hits` real NOT NULL DEFAULT 0,
                `version` text,
                `avg_tier` text
                -- kill / death / eigen / pagerank...
);
CREATE TABLE `ChampionKillMatrix` (
                -- `id` integer NOT NULL,
                `killer`        text NOT NULL,
                `victim`        text NOT NULL,
                `kills`         integer NOT NULL,
                `version`       text,
                `avg_tier`      text
                -- PRIMARY KEY(id)
);
CREATE TABLE `ChampionAssistMatrix` (
        -- `id` integer NOT NULL,
                `killer`        text NOT NULL, /*key*/
                `assist`        text NOT NULL, /*key*/
                `assists`       integer NOT NULL,
                `version`       text,
                `avg_tier`      text
                -- PRIMARY KEY(id)
);

CREATE INDEX index_Participant_match_id on Participant(match_id);
CREATE UNIQUE INDEX killer_victim on ChampionKillMatrix(killer, victim);
CREATE UNIQUE INDEX killer_assist on ChampionAssistMatrix(killer, assist);

-- INSERT INTO new.Participant SELECT * FROM old.Participant ORDER bY match_id ASC, CAST(participant_id AS INTEGER) ASC

