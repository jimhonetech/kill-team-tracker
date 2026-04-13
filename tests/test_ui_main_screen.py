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
