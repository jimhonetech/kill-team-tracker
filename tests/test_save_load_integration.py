"""Integration tests for save/load behavior across UI and state contracts."""

from __future__ import annotations

from app.state import GameState, PlayerScores
from app.ui.main_screen import MainGameScreen


def test_save_resume_round_trip_restores_state_and_ui() -> None:
    initial = GameState(
        turning_point=3,
        player_one=PlayerScores(
            command_points=2,
            tactical_vp=4,
            kill_vp=3,
            main_mission_vp=5,
            bonus_vp=2,
        ),
        player_two=PlayerScores(
            command_points=1,
            tactical_vp=2,
            kill_vp=6,
            main_mission_vp=4,
            bonus_vp=1,
        ),
        selected_operation="Secure Objective",
    )

    snapshot = initial.to_dict()
    stored: dict[str, str] = {}

    def save_handler(payload: dict[str, object]) -> None:
        stored["json"] = GameState.from_dict(payload).to_json()

    def resume_handler() -> dict[str, object]:
        return GameState.from_json(stored["json"]).to_dict()

    screen = MainGameScreen(
        initial,
        save_handler=save_handler,
        resume_handler=resume_handler,
    )

    screen._save_game()
    assert screen.persistence_status_label.text == "Game saved"

    screen.game_state.turning_point = 1
    screen.game_state.select_operation(None)
    screen.game_state.decrement_command_points("player_one", amount=2)
    screen.game_state.decrement_vp("player_one", "tactical_vp", amount=4)
    screen.game_state.decrement_vp("player_one", "kill_vp", amount=3)
    screen.game_state.decrement_vp("player_one", "main_mission_vp", amount=5)
    screen.game_state.set_bonus_vp("player_one", 0)
    screen.refresh_from_state()

    screen._resume_game()

    assert screen.persistence_status_label.text == "Game resumed"
    assert screen.game_state.to_dict() == snapshot
    assert screen.turning_point_label.text == "Turning Point 3"
    assert screen.operation_label.text == "Operation: Secure Objective"
    assert screen.score_value_labels[("player_one", "command_points")].text == "2"
    assert screen.score_value_labels[("player_one", "bonus_vp")].text == "2"


def test_resume_surfaces_deserialization_error_for_invalid_payload() -> None:
    def save_handler(_payload: dict[str, object]) -> None:
        return None

    def invalid_resume_handler() -> dict[str, object]:
        return {"schema_version": 1, "turning_point": 2, "players": []}

    screen = MainGameScreen(
        GameState(),
        save_handler=save_handler,
        resume_handler=invalid_resume_handler,
    )

    screen._resume_game()

    assert screen.persistence_status_label.text.startswith(
        "Resume failed: players must be a dictionary"
    )
