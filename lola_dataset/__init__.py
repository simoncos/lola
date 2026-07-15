"""LoLA-2016 dataset curation toolkit.

Modern (Python 3.9+) tooling to validate, profile, anonymize and export the
legacy lola.db SQLite archive (222k NA ranked matches, Pre-Season 2016).

Usage:
    python -m lola_dataset validate --db lola.db --out reports/validate.json
    python -m lola_dataset stats    --db lola.db --out reports/stats.json
    python -m lola_dataset export   --db lola.db --out parquet/ --salt SECRET
"""

__version__ = "0.1.0"

TABLES = [
    "Summoner",
    "Match",
    "MatchChampion",
    "FrameKillEvent",
    "Team",
    "TeamBan",
    "Participant",
    "ParticipantTimeline",
    "ChampionMatchStats",
    "ChampionKillMatrix",
    "ChampionAssistMatrix",
    "ChampionIncidenceMatrix",
]

# Match.duration is stored in MINUTES (verified on the real DB: range 7-87;
# the 2016 crawler stored Cassiopeia's duration in minutes, and the dataset
# predates the remake feature entirely). Matches shorter than this threshold
# are flagged as very short (early surrender / AFK-abandoned games).
SHORT_MATCH_MINUTES = 10
