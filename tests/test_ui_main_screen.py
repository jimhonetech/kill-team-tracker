"""UI smoke tests for MainGameScreen score sections."""

from app.state import GameState, PlayerScores
from app.state.models import TURN_MAX, TURN_MIN
from app.ui.main_screen import MainGameScreen
from app.ui.player_palette import (
    player_accent,
    player_button_text,
    player_surface,
    player_surface_selected,
)


def _advance_to_turning_point_four(screen: MainGameScreen, state: GameState) -> None:
    while state.turning_point < TURN_MAX:
        screen._adjust_turning_point(1)


def test_main_screen_renders_scores_from_state() -> None:
    state = GameState(
        player_one_team="Kommandos",
        player_two_team="Kasrkin",
        player_one=PlayerScores(
            command_points=2, tactical_vp=3, kill_vp=4, main_mission_vp=5
        ),
        player_two=PlayerScores(
            command_points=1, tactical_vp=6, kill_vp=7, main_mission_vp=8
        ),
    )

    screen = MainGameScreen(state)

    assert screen.title_label.text == "Gameplay"
    assert screen.matchup_label.text == "Kommandos vs Kasrkin"
    assert screen.score_value_labels[("player_one", "command_points")].text == "2"
    assert screen.score_value_labels[("player_one", "tactical_vp")].text == "3"
    assert screen.score_value_labels[("player_two", "kill_vp")].text == "7"
    assert screen.score_value_labels[("player_two", "main_mission_vp")].text == "8"


def test_main_screen_layout_is_focused_on_gameplay_controls() -> None:
    screen = MainGameScreen(GameState())

    assert screen.persistence_controls.parent is None
    assert screen.reset_controls.parent is None
    assert screen.end_game_controls.parent is None
    assert screen.end_game_summary.parent is None


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


def test_main_screen_uses_shared_player_palette_for_scores_and_selectors() -> None:
    state = GameState(
        end_game=True,
        player_one=PlayerScores(secret_op="tac_op"),
        player_two=PlayerScores(),
    )
    screen = MainGameScreen(state)

    assert tuple(screen.player_title_labels["player_one"].color) == player_accent(
        "player_one"
    )
    assert tuple(
        screen.score_title_labels[("player_two", "kill_vp")].color
    ) == player_accent("player_two")
    assert tuple(screen.total_value_labels["player_one"].color) == player_accent(
        "player_one"
    )

    selected_button = screen.secret_op_buttons[("player_one", "tac_op")]
    unselected_button = screen.secret_op_buttons[("player_one", "kill_op")]

    assert tuple(selected_button.background_color) == player_surface_selected(
        "player_one"
    )
    assert tuple(selected_button.color) == player_button_text(True)
    assert tuple(unselected_button.background_color) == player_surface("player_one")
    assert tuple(unselected_button.color) == player_button_text(False)


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

    assert state.turning_point == TURN_MAX
    assert state.end_game is False
    assert screen.turning_point_label.text == f"Turning Point {TURN_MAX}"
    assert screen.turning_point_increment_button.disabled is False
    assert tuple(screen.turning_point_increment_button.background_color) == (
        1,
        0.55,
        0,
        1,
    )


def test_tp_plus_button_turns_amber_at_turning_point_four() -> None:
    state = GameState(turning_point=3)
    screen = MainGameScreen(state)

    assert tuple(screen.turning_point_increment_button.background_color) == (
        1,
        1,
        1,
        1,
    )

    screen._adjust_turning_point(1)

    assert state.turning_point == TURN_MAX
    assert tuple(screen.turning_point_increment_button.background_color) == (
        1,
        0.55,
        0,
        1,
    )


def test_tp_plus_uses_handler_without_locking_gameplay_state() -> None:
    state = GameState(
        turning_point=TURN_MAX,
        player_one_team="Kommandos",
        player_two_team="Kasrkin",
    )
    captured = {"count": 0}

    def end_game_handler() -> None:
        captured["count"] += 1

    screen = MainGameScreen(state, end_game_handler=end_game_handler)

    screen._adjust_turning_point(1)

    assert captured["count"] == 1
    assert state.end_game is False
    assert state.turning_point == TURN_MAX
    assert screen.matchup_label.text == "Kommandos vs Kasrkin"


def test_main_screen_controls_respect_state_bounds() -> None:
    state = GameState(player_one=PlayerScores(command_points=6, tactical_vp=15))
    screen = MainGameScreen(state)

    screen._adjust_cp("player_one", 1)
    screen._adjust_vp("player_one", "tactical_vp", 1)
    screen._adjust_cp("player_one", -1)

    assert state.player_one.command_points == 5
    assert state.player_one.tactical_vp == 15


def test_tp_plus_without_handler_keeps_gameplay_state_unchanged() -> None:
    state = GameState(turning_point=TURN_MAX)
    screen = MainGameScreen(state)

    screen._adjust_turning_point(1)

    assert state.turning_point == TURN_MAX
    assert state.end_game is False
    assert screen.turning_point_label.text == f"Turning Point {TURN_MAX}"


def test_reset_confirm_calls_state_reset_and_updates_screen() -> None:
    state = GameState(
        turning_point=4,
        end_game=True,
        player_one_team="Kommandos",
        player_two_team="Kasrkin",
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
    assert tuple(screen.turning_point_increment_button.background_color) == (
        1,
        1,
        1,
        1,
    )
    assert screen.matchup_label.text == "Player One vs Player Two"


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
