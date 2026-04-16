"""State-level tests for completed match archives and stats aggregation."""

from __future__ import annotations

import pytest

from app.state import (
    ARCHIVE_SCHEMA_VERSION,
    CompletedMatchArchive,
    GameState,
    PlayerScores,
    build_stats_summary,
    build_win_rate_summary,
    migrate_history_payload,
)


def _state(
    *,
    p1_team: str = "Kommandos",
    p2_team: str = "Kasrkin",
    p1: PlayerScores | None = None,
    p2: PlayerScores | None = None,
) -> GameState:
    return GameState(
        turning_point=4,
        end_game=True,
        player_one_team=p1_team,
        player_two_team=p2_team,
        player_one=p1 or PlayerScores(tactical_vp=4, kill_vp=2, main_mission_vp=1),
        player_two=p2 or PlayerScores(tactical_vp=2, kill_vp=1, main_mission_vp=1),
    )


def _scores(
    *,
    tactical_vp: int = 0,
    kill_vp: int = 0,
    crit_vp: int = 0,
    bonus_vp: int = 0,
    secret_op: str | None = None,
) -> PlayerScores:
    return PlayerScores(
        tactical_vp=tactical_vp,
        kill_vp=kill_vp,
        main_mission_vp=crit_vp,
        bonus_vp=bonus_vp,
        secret_op=secret_op,
    )


def test_completed_match_archive_from_game_state_round_trip() -> None:
    state = _state()

    archive = CompletedMatchArchive.from_game_state(
        state, archived_at="2026-04-15T10:00:00Z"
    )
    payload = archive.to_dict()
    restored = CompletedMatchArchive.from_dict(payload)

    assert payload["archive_schema_version"] == ARCHIVE_SCHEMA_VERSION
    assert restored.archived_at == "2026-04-15T10:00:00Z"
    assert restored.winner == "player_one"
    assert restored.final_scores == {"player_one": 7, "player_two": 4}
    assert restored.game_snapshot == state.to_dict()


def test_migrate_history_payload_handles_missing_payload() -> None:
    migrated = migrate_history_payload(None)

    assert migrated == {"schema_version": 1, "matches": []}


def test_migrate_history_payload_accepts_legacy_list_of_game_states() -> None:
    state = _state()
    migrated = migrate_history_payload([state.to_dict()])

    assert migrated["schema_version"] == 1
    matches = migrated["matches"]
    assert isinstance(matches, list)
    assert len(matches) == 1
    assert matches[0]["winner"] == "player_one"
    assert matches[0]["game_snapshot"] == state.to_dict()


def test_migrate_history_payload_rejects_invalid_match_item() -> None:
    with pytest.raises(ValueError, match="history match at index 0"):
        migrate_history_payload(["bad-item"])


def test_migrate_history_payload_rejects_unsupported_schema_version() -> None:
    with pytest.raises(ValueError, match="unsupported history schema_version"):
        migrate_history_payload({"schema_version": 99, "matches": []})


def test_build_stats_summary_handles_empty_history() -> None:
    summary = build_stats_summary([])

    assert summary["total_matches"] == 0
    assert summary["draws"] == 0
    assert summary["player_slots"] == {
        "player_one": {
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "matches": 0,
            "win_percentage": 0.0,
        },
        "player_two": {
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "matches": 0,
            "win_percentage": 0.0,
        },
    }
    assert summary["teams"] == {}
    assert summary["primary_ops"]["player_one"]["revealed_primary_ops"] == 0
    assert summary["primary_ops"]["player_one"]["most_successful"]["op"] is None
    assert summary["op_buckets"]["tac_op"]["player_one"] == {
        "matches": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "win_percentage": 0.0,
        "total_vp": 0,
        "average_vp": 0.0,
        "selected_as_primary": 0,
        "total_bonus_vp_when_primary": 0,
        "average_bonus_vp_when_primary": 0.0,
    }


def test_build_stats_summary_handles_wins_draws_missing_values_and_op_analytics() -> (
    None
):
    p1_win = CompletedMatchArchive.from_game_state(
        _state(
            p1_team="Kommandos",
            p2_team="Kasrkin",
            p1=_scores(tactical_vp=6, kill_vp=1, bonus_vp=3, secret_op="tac_op"),
            p2=_scores(tactical_vp=1, kill_vp=2, bonus_vp=1, secret_op="kill_op"),
        ),
        archived_at="2026-04-15T10:00:00Z",
    )
    p2_win = CompletedMatchArchive.from_game_state(
        _state(
            p1_team="Kasrkin",
            p2_team="Kommandos",
            p1=_scores(tactical_vp=1, kill_vp=2, bonus_vp=1, secret_op="kill_op"),
            p2=_scores(tactical_vp=6, kill_vp=1, bonus_vp=3, secret_op="tac_op"),
        ),
        archived_at="2026-04-15T10:05:00Z",
    )
    draw = CompletedMatchArchive.from_game_state(
        _state(
            p1_team=None,
            p2_team="Kommandos",
            p1=_scores(
                tactical_vp=1,
                kill_vp=1,
                crit_vp=4,
                bonus_vp=2,
                secret_op="crit_op",
            ),
            p2=_scores(tactical_vp=4, kill_vp=2, crit_vp=2, bonus_vp=0),
        ),
        archived_at="2026-04-15T10:10:00Z",
    )

    summary = build_stats_summary([p1_win, p2_win, draw])

    assert summary["total_matches"] == 3
    assert summary["draws"] == 1

    player_slots = summary["player_slots"]
    assert player_slots["player_one"]["wins"] == 1
    assert player_slots["player_one"]["draws"] == 1
    assert player_slots["player_one"]["losses"] == 1
    assert player_slots["player_one"]["win_percentage"] == 33.33
    assert player_slots["player_two"]["wins"] == 1
    assert player_slots["player_two"]["draws"] == 1
    assert player_slots["player_two"]["losses"] == 1
    assert player_slots["player_two"]["win_percentage"] == 33.33

    teams = summary["teams"]
    kommandos = teams["Kommandos"]
    assert kommandos["overall"]["matches"] == 3
    assert kommandos["overall"]["wins"] == 2
    assert kommandos["overall"]["draws"] == 1
    assert kommandos["overall"]["losses"] == 0
    assert kommandos["overall"]["win_percentage"] == 66.67
    assert kommandos["player_one"]["matches"] == 1
    assert kommandos["player_one"]["wins"] == 1
    assert kommandos["player_two"]["matches"] == 2
    assert kommandos["player_two"]["wins"] == 1
    assert kommandos["player_two"]["draws"] == 1

    kasrkin = teams["Kasrkin"]
    assert kasrkin["overall"]["matches"] == 2
    assert kasrkin["overall"]["wins"] == 0
    assert kasrkin["overall"]["losses"] == 2
    assert kasrkin["overall"]["win_percentage"] == 0.0

    player_one_primary = summary["primary_ops"]["player_one"]
    assert player_one_primary["player_entries"] == 3
    assert player_one_primary["revealed_primary_ops"] == 3
    assert player_one_primary["missing_primary_ops"] == 0
    assert player_one_primary["most_successful"]["op"] == "tac_op"
    assert player_one_primary["ops"]["tac_op"] == {
        "label": "Tac Op",
        "picks": 1,
        "matches": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "win_percentage": 100.0,
        "total_selected_vp": 6,
        "average_selected_vp": 6.0,
        "total_bonus_vp": 3,
        "average_bonus_vp": 3.0,
    }
    assert player_one_primary["ops"]["crit_op"]["draws"] == 1
    assert player_one_primary["ops"]["kill_op"]["losses"] == 1

    player_two_primary = summary["primary_ops"]["player_two"]
    assert player_two_primary["player_entries"] == 3
    assert player_two_primary["revealed_primary_ops"] == 2
    assert player_two_primary["missing_primary_ops"] == 1
    assert player_two_primary["most_successful"]["op"] == "tac_op"
    assert player_two_primary["ops"]["kill_op"]["wins"] == 0
    assert player_two_primary["ops"]["kill_op"]["losses"] == 1

    combined_primary = summary["primary_ops"]["combined"]
    assert combined_primary["player_entries"] == 6
    assert combined_primary["revealed_primary_ops"] == 5
    assert combined_primary["missing_primary_ops"] == 1
    assert combined_primary["most_successful"]["op"] == "tac_op"
    assert combined_primary["most_successful"]["tied_ops"] == ["tac_op"]
    assert combined_primary["ops"]["tac_op"]["picks"] == 2
    assert combined_primary["ops"]["tac_op"]["wins"] == 2
    assert combined_primary["ops"]["tac_op"]["average_selected_vp"] == 6.0
    assert combined_primary["ops"]["kill_op"]["picks"] == 2
    assert combined_primary["ops"]["kill_op"]["losses"] == 2
    assert combined_primary["ops"]["crit_op"]["draws"] == 1

    tac_bucket = summary["op_buckets"]["tac_op"]
    assert tac_bucket["label"] == "Tac Op"
    assert tac_bucket["player_one"] == {
        "matches": 3,
        "wins": 1,
        "draws": 1,
        "losses": 1,
        "win_percentage": 33.33,
        "total_vp": 8,
        "average_vp": 2.67,
        "selected_as_primary": 1,
        "total_bonus_vp_when_primary": 3,
        "average_bonus_vp_when_primary": 3.0,
    }
    assert tac_bucket["combined"]["matches"] == 6
    assert tac_bucket["combined"]["total_vp"] == 19
    assert tac_bucket["combined"]["average_vp"] == 3.17
    assert tac_bucket["combined"]["selected_as_primary"] == 2
    assert summary["op_buckets"]["crit_op"]["player_two"]["selected_as_primary"] == 0


def test_build_stats_summary_uses_canonical_op_order_for_most_successful_ties() -> None:
    tac_win = CompletedMatchArchive.from_game_state(
        _state(
            p1=_scores(tactical_vp=6, bonus_vp=3, secret_op="tac_op"),
            p2=_scores(tactical_vp=1),
        ),
        archived_at="2026-04-15T11:00:00Z",
    )
    kill_win = CompletedMatchArchive.from_game_state(
        _state(
            p1=_scores(kill_vp=6, bonus_vp=3, secret_op="kill_op"),
            p2=_scores(kill_vp=1),
        ),
        archived_at="2026-04-15T11:05:00Z",
    )

    summary = build_stats_summary([tac_win, kill_win])

    player_one_primary = summary["primary_ops"]["player_one"]
    assert player_one_primary["most_successful"]["op"] == "tac_op"
    assert player_one_primary["most_successful"]["tied_ops"] == [
        "tac_op",
        "kill_op",
    ]
    assert player_one_primary["most_successful"]["sort_fields"] == [
        "win_percentage",
        "wins",
        "average_selected_vp",
        "average_bonus_vp",
        "picks",
        "op_order",
    ]


def test_build_win_rate_summary_remains_compatible_wrapper() -> None:
    summary = build_win_rate_summary([])

    assert summary["total_matches"] == 0
    assert "primary_ops" in summary
    assert "op_buckets" in summary
