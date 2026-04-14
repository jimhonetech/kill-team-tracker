"""UI smoke tests for MainGameScreen score sections."""

from app.state import GameState, PlayerScores
from app.state.models import TURN_MAX, TURN_MIN
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


def test_turning_point_controls_update_state_and_respect_bounds() -> None:
    state = GameState()
    screen = MainGameScreen(state)

    assert screen.turning_point_label.text == f"Turning Point {TURN_MIN}"

    for expected_turn in range(TURN_MIN + 1, TURN_MAX + 1):
        screen._adjust_turning_point(1)
        assert state.turning_point == expected_turn
        assert screen.turning_point_label.text == f"Turning Point {expected_turn}"

    for expected_turn in range(TURN_MAX - 1, TURN_MIN - 1, -1):
        screen._adjust_turning_point(-1)
        assert state.turning_point == expected_turn
        assert screen.turning_point_label.text == f"Turning Point {expected_turn}"

    screen._adjust_turning_point(-1)
    assert state.turning_point == TURN_MIN
    assert screen.turning_point_label.text == f"Turning Point {TURN_MIN}"

    for _ in range(TURN_MIN, TURN_MAX):
        screen._adjust_turning_point(1)

    screen._adjust_turning_point(1)

    assert state.turning_point == TURN_MAX
    assert state.end_game is True
    assert screen.turning_point_label.text == "End Game"
    assert screen.turning_point_decrement_button.disabled is True
    assert screen.turning_point_increment_button.disabled is True


def test_main_screen_controls_respect_state_bounds() -> None:
    state = GameState(player_one=PlayerScores(command_points=6, tactical_vp=15))
    screen = MainGameScreen(state)

    screen._adjust_cp("player_one", 1)
    screen._adjust_vp("player_one", "tactical_vp", 1)
    screen._adjust_cp("player_one", -1)

    assert state.player_one.command_points == 5
    assert state.player_one.tactical_vp == 15


def test_end_game_trigger_shows_secret_op_buttons_and_updates_each_player() -> None:
    state = GameState(turning_point=TURN_MAX)
    screen = MainGameScreen(state)

    screen._adjust_turning_point(1)
    screen._set_secret_op("player_one", "tac_op")
    screen._set_secret_op("player_two", "crit_op")

    assert state.end_game is True
    assert state.player_one.secret_op == "tac_op"
    assert state.player_two.secret_op == "crit_op"
    assert screen.end_game_controls.height > 0
    assert screen.secret_op_status_labels["player_one"].text == "Selected: Tac Op"
    assert screen.secret_op_status_labels["player_two"].text == "Selected: Crit Op"
    assert (
        tuple(screen.secret_op_buttons[("player_one", "tac_op")].background_color)
        == MainGameScreen.SECRET_OP_SELECTED_COLOR
    )
    assert (
        tuple(screen.secret_op_buttons[("player_one", "kill_op")].background_color)
        == MainGameScreen.SECRET_OP_BUTTON_COLOR
    )


def test_bonus_vp_controls_remain_usable_in_end_game() -> None:
    state = GameState(
        turning_point=TURN_MAX,
        end_game=True,
        player_one=PlayerScores(tactical_vp=4, kill_vp=3, main_mission_vp=2),
        player_two=PlayerScores(tactical_vp=1, kill_vp=1, main_mission_vp=1),
    )
    screen = MainGameScreen(state)

    assert screen.total_value_labels["player_one"].text == "9"

    screen._adjust_bonus("player_one", 1)
    screen._adjust_bonus("player_one", 1)

    assert state.final_scores()["player_one"] == 11
    assert screen.total_value_labels["player_one"].text == "11"


def test_end_game_summary_shows_only_after_both_players_reveal() -> None:
    state = GameState(turning_point=TURN_MAX, end_game=True)
    screen = MainGameScreen(state)

    assert screen.end_game_summary.height == 0
    assert screen.end_game_summary.opacity == 0

    screen._set_secret_op("player_one", "tac_op")
    assert screen.end_game_summary.height == 0
    assert screen.end_game_summary.opacity == 0

    screen._set_secret_op("player_two", "kill_op")
    assert screen.end_game_summary.height > 0
    assert screen.end_game_summary.opacity == 1


def test_end_game_summary_displays_primary_bonus_formula_and_total() -> None:
    state = GameState(
        turning_point=TURN_MAX,
        end_game=True,
        player_one=PlayerScores(
            tactical_vp=5, kill_vp=3, main_mission_vp=2, bonus_vp=1
        ),
        player_two=PlayerScores(tactical_vp=1, kill_vp=4, main_mission_vp=6),
    )
    screen = MainGameScreen(state)

    screen._set_secret_op("player_one", "tac_op")
    screen._set_secret_op("player_two", "crit_op")

    player_one_summary = screen.summary_player_labels["player_one"].text
    player_two_summary = screen.summary_player_labels["player_two"].text

    assert "Player One Summary" in player_one_summary
    assert "Tac Op: 5 VP [PRIMARY]" in player_one_summary
    assert "Kill Op: 3 VP" in player_one_summary
    assert "Crit Op: 2 VP" in player_one_summary
    assert (
        "Primary Op: Tac Op (5 VP) -> Formula Bonus: 3 "
        "(calculate_bonus_vp = ceil(5/2))"
    ) in player_one_summary
    assert "Formula Total: 10 + 3 = 13" in player_one_summary
    assert "Tracked Total: 10 + 1 = 11" in player_one_summary

    assert "Player Two Summary" in player_two_summary
    assert "Tac Op: 1 VP" in player_two_summary
    assert "Kill Op: 4 VP" in player_two_summary
    assert "Crit Op: 6 VP [PRIMARY]" in player_two_summary
    assert (
        "Primary Op: Crit Op (6 VP) -> Formula Bonus: 3 "
        "(calculate_bonus_vp = ceil(6/2))"
    ) in player_two_summary
    assert "Formula Total: 11 + 3 = 14" in player_two_summary
    assert "Tracked Total: 11 + 0 = 11" in player_two_summary


def test_reset_confirm_calls_state_reset_and_updates_screen() -> None:
    state = GameState(
        turning_point=4,
        end_game=True,
        player_one=PlayerScores(command_points=4, tactical_vp=5, kill_vp=6),
        player_two=PlayerScores(secret_op="kill_op"),
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
    assert screen.turning_point_label.text == "Turning Point 1"
    assert screen.end_game_controls.height == 0


def test_reset_cancel_path_does_not_mutate_state() -> None:
    state = GameState(player_one=PlayerScores(command_points=2, tactical_vp=3))
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
