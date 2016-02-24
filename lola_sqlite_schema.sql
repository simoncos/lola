	BEGIN TRANSACTION;
	CREATE TABLE `Team` (
		-- `id`	integer NOT NULL,
		`match_id`	text NOT NULL, /*key*/
		`side`	text NOT NULL, /*key*/
		`dragon_kills` integer NOT NULL,
		`baron_kills` integer NOT NULL,
		`win`	integer NOT NULL
		-- PRIMARY KEY(id)
	);
	CREATE TABLE `TeamBan` (
		-- `id`	integer NOT NULL,
		`match_id`	text NOT NULL, /*key*/
		`side`	text NOT NULL, /*key*/
		`ban` text NOT NULL /*key*/
		-- PRIMARY KEY(id)
	);
	CREATE TABLE `Summoner` (
		-- `id`	integer NOT NULL,
		`summoner_id`	text NOT NULL UNIQUE, /*key*/
		`summoner_name`	text NOT NULL,
		`is_crawled`	integer NOT NULL
		-- PRIMARY KEY(id)
	);
	CREATE TABLE `Participant` (
		-- `id`	integer NOT NULL,
		`summoner_id`	text NOT NULL, /*key*/
		`match_id`	text NOT NULL, /*key*/
		`participant_id` text NOT NULL,
		`side`	text NOT NULL, 
		`champion`	text NOT NULL,
		`previous_season_tier`	text,
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
		`participant_win` integer NOT NULL

		-- PRIMARY KEY(id)
	);
	CREATE TABLE `ParticipantTimeline` (
		-- `id`	integer NOT NULL,
		`summoner_id`	text NOT NULL, /*key*/
		`match_id`	text NOT NULL, /*key*/
		`delta` text NOT NULL, /*key*/
		`side`	text NOT NULL, 		
		`participant_id` text NOT NULL,
		`role` text NOT NULL,
		`lane` text NOT NULL,

		`creeps_per_min_delta` real,
		`cs_diff_per_min_delta` real,
		`gold_per_min_delta` real,
		`xp_diff_per_min_delta` real,
		`xp_per_min_delta` real,
		`damage_taken_per_min_delta` real,
		`damage_taken_diff_per_min_delta` real
		-- PRIMARY KEY(id)
	);
	CREATE TABLE `Match` (
		-- `id`	integer NOT NULL,
		`match_id`	text NOT NULL UNIQUE, /*key*/
		`version` text NOT NULL,	
		`duration` integer NOT NULL,
		-- `season` text NOT NULL,
		`data` text,
		`is_crawled`	integer NOT NULL
		-- PRIMARY KEY(id)
	);
	CREATE TABLE `FrameKillEvent` (
		-- `id`	integer NOT NULL,
		`match_id`	text NOT NULL, /*key*/
		`happen`	integer NOT NULL, /*key*/
		`victim` text NOT NULL, /*key*/
		`minute`	integer NOT NULL,
		`killer` text NOT NULL,
		`assist` text
		-- PRIMARY KEY(id)
	);
	COMMIT;
