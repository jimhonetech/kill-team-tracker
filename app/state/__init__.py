"""State models and contracts for Kill Team Tracker."""

from .history import (
    ARCHIVE_SCHEMA_VERSION,
    HISTORY_SCHEMA_VERSION,
    CompletedMatchArchive,
    build_stats_summary,
    build_win_rate_summary,
    load_archives_from_payload,
    migrate_history_payload,
)
from .models import STARTER_KILL_TEAMS, GameState, PlayerScores

__all__ = [
    "ARCHIVE_SCHEMA_VERSION",
    "HISTORY_SCHEMA_VERSION",
    "CompletedMatchArchive",
    "build_stats_summary",
    "GameState",
    "PlayerScores",
    "STARTER_KILL_TEAMS",
    "build_win_rate_summary",
    "load_archives_from_payload",
    "migrate_history_payload",
]
