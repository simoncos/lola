"""LoLA-2016 dataset curation toolkit.

Modern (Python 3.10+) tooling to validate, profile, pseudonymize and export the
legacy lola.db SQLite archive (222k NA ranked matches, Pre-Season 2016).

Usage:
    python -m lola_dataset validate --db lola.db --out reports/validate.json
    python -m lola_dataset stats    --db lola.db --out reports/stats.json
    python -m lola_dataset export   --db lola.db --out parquet/ --salt-file SALT_PRIVATE.txt
"""

__version__ = "0.2.0"

REQUIRED_TABLES = [
    "Summoner",
    "Match",
    "FrameKillEvent",
    "Team",
    "TeamBan",
    "Participant",
    "ParticipantTimeline",
]

OPTIONAL_LEGACY_TABLES = [
    "MatchChampion",
    "ChampionMatchStats",
    "ChampionKillMatrix",
    "ChampionAssistMatrix",
    "ChampionIncidenceMatrix",
]

TABLES = REQUIRED_TABLES + OPTIONAL_LEGACY_TABLES

# Match.duration is stored in MINUTES (verified on the real DB: range 7-87;
# the 2016 crawler stored Cassiopeia's duration in minutes, and the dataset
# predates the remake feature entirely). Matches shorter than this threshold
# are flagged as very short (early surrender / AFK-abandoned games).
SHORT_MATCH_MINUTES = 10
