"""Tests for GameState model and serialization contract."""

import pytest

from app.state import GameState, PlayerScores


def test_game_state_initializes_with_valid_defaults() -> None:
    state = GameState()

    assert state.turning_point == 1
    assert state.player_one.command_points == 0
    assert state.player_two.main_mission_vp == 0


def test_game_state_rejects_invalid_turning_point() -> None:
    with pytest.raises(ValueError, match="turning_point"):
        GameState(turning_point=0)

    with pytest.raises(ValueError, match="turning_point"):
        GameState(turning_point=5)


def test_player_scores_reject_invalid_ranges() -> None:
    with pytest.raises(ValueError, match="command_points"):
        PlayerScores(command_points=7)

    with pytest.raises(ValueError, match="tactical_vp"):
        PlayerScores(tactical_vp=16)


def test_game_state_serialization_round_trip() -> None:
    original = GameState(
        turning_point=3,
        player_one=PlayerScores(
            command_points=2, tactical_vp=4, kill_vp=3, main_mission_vp=5
        ),
        player_two=PlayerScores(
            command_points=1, tactical_vp=2, kill_vp=6, main_mission_vp=4
        ),
    )

    payload = original.to_json()
    restored = GameState.from_json(payload)

    assert restored.to_dict() == original.to_dict()


def test_game_state_from_dict_rejects_invalid_player_payload() -> None:
    with pytest.raises(ValueError, match="players"):
        GameState.from_dict({"schema_version": 1, "turning_point": 2, "players": []})


def test_game_state_from_dict_accepts_supported_schema_version() -> None:
    restored = GameState.from_dict(
        {
            "schema_version": 1,
            "turning_point": 2,
            "players": {
                "player_one": {"command_points": 1},
                "player_two": {"command_points": 2},
            },
        }
    )

    assert restored.turning_point == 2
    assert restored.player_one.command_points == 1
    assert restored.player_two.command_points == 2


def test_game_state_from_dict_rejects_missing_schema_version() -> None:
    with pytest.raises(ValueError, match="schema_version is required"):
        GameState.from_dict({"turning_point": 2, "players": {}})


def test_game_state_from_dict_rejects_unsupported_schema_version() -> None:
    with pytest.raises(ValueError, match="unsupported schema_version: 2; expected 1"):
        GameState.from_dict({"schema_version": 2, "turning_point": 2, "players": {}})


def test_increment_decrement_command_points_respect_bounds() -> None:
    state = GameState(player_one=PlayerScores(command_points=5))

    assert state.increment_command_points("player_one") == 6
    assert state.increment_command_points("player_one") == 6
    assert state.decrement_command_points("player_one", amount=10) == 0
    assert state.decrement_command_points("player_one") == 0


def test_increment_decrement_vp_respect_bounds() -> None:
    state = GameState(player_two=PlayerScores(tactical_vp=14))

    assert state.increment_vp("player_two", "tactical_vp", amount=2) == 15
    assert state.decrement_vp("player_two", "tactical_vp", amount=20) == 0


def test_score_update_methods_validate_inputs() -> None:
    state = GameState()

    with pytest.raises(ValueError, match="unknown player"):
        state.increment_command_points("player_three")

    with pytest.raises(ValueError, match="unknown VP category"):
        state.increment_vp("player_one", "secondary_vp")

    with pytest.raises(ValueError, match="amount must be positive"):
        state.decrement_command_points("player_one", amount=0)


def test_operation_selection_and_bonus_round_trip() -> None:
    state = GameState()

    assert state.select_operation("  Secure Objective  ") == "Secure Objective"
    assert state.set_bonus_vp("player_one", 3) == 3

    payload = state.to_json()
    restored = GameState.from_json(payload)

    assert restored.selected_operation == "Secure Objective"
    assert restored.player_one.bonus_vp == 3


def test_operation_selection_rejects_empty_string() -> None:
    state = GameState()

    with pytest.raises(ValueError, match="operation must be a non-empty string"):
        state.select_operation("   ")


def test_bonus_vp_and_final_scores_include_bonus_total() -> None:
    state = GameState(
        player_one=PlayerScores(tactical_vp=4, kill_vp=5, main_mission_vp=3),
        player_two=PlayerScores(tactical_vp=2, kill_vp=1, main_mission_vp=6),
    )

    assert state.set_bonus_vp("player_one", 20) == 15
    assert state.set_bonus_vp("player_two", -5) == 0

    assert state.total_vp("player_one") == 27
    assert state.total_vp("player_two") == 9
    assert state.final_scores() == {"player_one": 27, "player_two": 9}


def test_reset_game_restores_canonical_initial_state() -> None:
    state = GameState(
        turning_point=4,
        player_one=PlayerScores(
            command_points=5,
            tactical_vp=7,
            kill_vp=6,
            main_mission_vp=8,
            bonus_vp=4,
        ),
        player_two=PlayerScores(
            command_points=3,
            tactical_vp=4,
            kill_vp=5,
            main_mission_vp=6,
            bonus_vp=2,
        ),
        selected_operation="Secure Objective",
    )

    state.reset_game()

    assert state.to_dict() == GameState().to_dict()


def test_reset_game_clears_operation_and_bonus_fields() -> None:
    state = GameState(selected_operation="Infiltration")
    state.set_bonus_vp("player_one", 5)

    state.reset_game()

    assert state.selected_operation is None
    assert state.player_one.bonus_vp == 0
    assert state.player_two.bonus_vp == 0


def test_game_state_from_json_rejects_invalid_json_payload() -> None:
    with pytest.raises(ValueError, match="JSON payload is invalid"):
        GameState.from_json("{bad json")


def test_game_state_from_json_rejects_non_object_payload() -> None:
    with pytest.raises(ValueError, match="must decode to an object"):
        GameState.from_json("[]")


def test_game_state_from_dict_requires_turning_point_and_players() -> None:
    with pytest.raises(ValueError, match="turning_point is required"):
        GameState.from_dict({"schema_version": 1, "players": {}})

    with pytest.raises(ValueError, match="players is required"):
        GameState.from_dict({"schema_version": 1, "turning_point": 1})
