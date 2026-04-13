"""UI smoke tests for MainGameScreen score sections."""

from app.state import GameState, PlayerScores
from app.ui.main_screen import MainGameScreen


def test_main_screen_renders_scores_from_state() -> None:
    state = GameState(
        player_one=PlayerScores(
            command_points=2, tactical_vp=3, kill_vp=4, main_mission_vp=5
        ),
        player_two=PlayerScores(
            command_points=1, tactical_vp=6, kill_vp=7, main_mission_vp=8
        ),
    )

    screen = MainGameScreen(state)

    assert screen.score_value_labels[("player_one", "command_points")].text == "2"
    assert screen.score_value_labels[("player_one", "tactical_vp")].text == "3"
    assert screen.score_value_labels[("player_two", "kill_vp")].text == "7"
    assert screen.score_value_labels[("player_two", "main_mission_vp")].text == "8"


def test_main_screen_controls_update_state_and_labels() -> None:
    state = GameState()
    screen = MainGameScreen(state)

    screen._adjust_cp("player_one", 1)
    screen._adjust_vp("player_one", "tactical_vp", 1)
    screen._adjust_vp("player_two", "kill_vp", 1)

    assert state.player_one.command_points == 1
    assert state.player_one.tactical_vp == 1
    assert state.player_two.kill_vp == 1

    assert screen.score_value_labels[("player_one", "command_points")].text == "1"
    assert screen.score_value_labels[("player_one", "tactical_vp")].text == "1"
    assert screen.score_value_labels[("player_two", "kill_vp")].text == "1"


def test_main_screen_controls_respect_state_bounds() -> None:
    state = GameState(player_one=PlayerScores(command_points=6, tactical_vp=15))
    screen = MainGameScreen(state)

    screen._adjust_cp("player_one", 1)
    screen._adjust_vp("player_one", "tactical_vp", 1)
    screen._adjust_cp("player_one", -1)

    assert state.player_one.command_points == 5
    assert state.player_one.tactical_vp == 15


def test_operation_selection_persists_in_state() -> None:
    state = GameState()
    screen = MainGameScreen(state)

    screen._set_operation("Recon Sweep")

    assert state.selected_operation == "Recon Sweep"
    assert screen.operation_label.text == "Operation: Recon Sweep"


def test_operation_selection_affects_displayed_totals_via_state_outputs() -> None:
    state = GameState(
        player_one=PlayerScores(tactical_vp=4, kill_vp=3, main_mission_vp=2),
        player_two=PlayerScores(tactical_vp=1, kill_vp=1, main_mission_vp=1),
    )
    screen = MainGameScreen(state)

    assert screen.total_value_labels["player_one"].text == "9"

    screen._adjust_bonus("player_one", 1)
    assert screen.total_value_labels["player_one"].text == "9"

    screen._set_operation("Secure Objective")
    screen._adjust_bonus("player_one", 1)
    screen._adjust_bonus("player_one", 1)

    assert state.selected_operation == "Secure Objective"
    assert state.final_scores()["player_one"] == 11
    assert screen.total_value_labels["player_one"].text == "11"


def test_reset_confirm_calls_state_reset_and_updates_screen() -> None:
    state = GameState(
        turning_point=4,
        player_one=PlayerScores(command_points=4, tactical_vp=5, kill_vp=6),
        selected_operation="Recon Sweep",
    )
    state.set_bonus_vp("player_one", 3)

    screen = MainGameScreen(state)

    screen._request_reset()
    assert screen.reset_pending is True
    assert screen.reset_status_label.text == "Confirm reset?"

    screen._confirm_reset()

    assert screen.reset_pending is False
    assert state.to_dict() == GameState().to_dict()
    assert screen.score_value_labels[("player_one", "command_points")].text == "0"
    assert screen.operation_label.text == "Operation: None"


def test_reset_cancel_path_does_not_mutate_state() -> None:
    state = GameState(
        player_one=PlayerScores(command_points=2, tactical_vp=3),
        selected_operation="Secure Objective",
    )
    snapshot = state.to_dict()
    screen = MainGameScreen(state)

    screen._request_reset()
    screen._cancel_reset()

    assert screen.reset_pending is False
    assert state.to_dict() == snapshot


def test_save_and_resume_controls_trigger_handlers_and_status() -> None:
    state = GameState(player_one=PlayerScores(command_points=2))
    captured: dict[str, object] = {}

    def save_handler(payload: dict[str, object]) -> None:
        captured.update(payload)

    def resume_handler() -> dict[str, object]:
        payload = state.to_dict()
        payload["turning_point"] = 3
        players = payload["players"]
        assert isinstance(players, dict)
        player_one = players["player_one"]
        assert isinstance(player_one, dict)
        player_one["command_points"] = 5
        return payload

    screen = MainGameScreen(
        state, save_handler=save_handler, resume_handler=resume_handler
    )

    screen._save_game()
    assert captured["turning_point"] == 1
    assert screen.persistence_status_label.text == "Game saved"

    screen._resume_game()
    assert screen.game_state.turning_point == 3
    assert screen.game_state.player_one.command_points == 5
    assert screen.persistence_status_label.text == "Game resumed"


def test_save_resume_failure_states_are_surfaced() -> None:
    def failing_save(_payload: dict[str, object]) -> None:
        raise RuntimeError("disk full")

    def failing_resume() -> dict[str, object]:
        raise RuntimeError("no save found")

    screen = MainGameScreen(
        GameState(),
        save_handler=failing_save,
        resume_handler=failing_resume,
    )

    screen._save_game()
    assert screen.persistence_status_label.text.startswith("Save failed: disk full")

    screen._resume_game()
    assert screen.persistence_status_label.text.startswith(
        "Resume failed: no save found"
    )
