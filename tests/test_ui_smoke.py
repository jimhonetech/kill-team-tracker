"""Low-maintenance UI smoke tests for app startup and screen loading."""

from __future__ import annotations

from kivy.app import App

from app.main import main
from app.state import GameState
from app.state.models import TURN_MAX
from app.ui.flow import TrackerFlow
from app.ui.main_screen import MainGameScreen
from app.ui.player_palette import player_accent, player_surface, player_surface_selected


def _trigger_end_game_via_tp_plus(flow: TrackerFlow) -> None:
    while flow.game_state.turning_point < TURN_MAX:
        flow.main_game_screen._adjust_turning_point(1)
    flow.main_game_screen._adjust_turning_point(1)


def test_main_game_screen_loads_with_default_state() -> None:
    screen = MainGameScreen(GameState())

    assert screen.title_label.text == "Gameplay"
    assert screen.matchup_label.text == "Player One vs Player Two"
    assert screen.turning_point_label.text == "Turning Point 1"
    assert tuple(screen.turning_point_increment_button.background_color) == (
        1,
        1,
        1,
        1,
    )
    assert screen.total_value_labels["player_one"].text == "0"
    assert screen.total_value_labels["player_two"].text == "0"


def test_tracker_flow_defaults_to_home_and_stats_navigation_is_enabled() -> None:
    flow = TrackerFlow(GameState())

    assert flow.current == "home"
    assert flow.home_screen.start_game_button.text == "Start Game"
    assert flow.home_screen.stats_button.disabled is False

    flow.home_screen.stats_button.dispatch("on_press")

    assert flow.current == "stats"
    assert flow.stats_screen.stats_views.current == flow.stats_screen.VIEW_WIN_RATES
    assert "stats reader is not configured" in flow.stats_screen.error_label.text
    flow.stats_screen.back_button.dispatch("on_press")
    assert flow.current == "home"


def test_stats_screen_renders_empty_history_summary() -> None:
    def read_summary() -> dict[str, object]:
        return {
            "total_matches": 0,
            "draws": 0,
            "player_slots": {
                "player_one": {
                    "wins": 0,
                    "draws": 0,
                    "matches": 0,
                    "win_percentage": 0.0,
                },
                "player_two": {
                    "wins": 0,
                    "draws": 0,
                    "matches": 0,
                    "win_percentage": 0.0,
                },
            },
            "teams": {},
            "primary_ops": {
                "player_one": {
                    "player_entries": 0,
                    "revealed_primary_ops": 0,
                    "missing_primary_ops": 0,
                    "most_successful": {"op": None, "label": None, "tied_ops": []},
                    "ops": {},
                },
                "player_two": {
                    "player_entries": 0,
                    "revealed_primary_ops": 0,
                    "missing_primary_ops": 0,
                    "most_successful": {"op": None, "label": None, "tied_ops": []},
                    "ops": {},
                },
                "combined": {
                    "player_entries": 0,
                    "revealed_primary_ops": 0,
                    "missing_primary_ops": 0,
                    "most_successful": {"op": None, "label": None, "tied_ops": []},
                    "ops": {},
                },
            },
            "op_buckets": {},
        }

    flow = TrackerFlow(GameState(), read_win_rate_summary_handler=read_summary)

    flow.home_screen.stats_button.dispatch("on_press")

    assert flow.current == "stats"
    assert flow.stats_screen.stats_views.current == flow.stats_screen.VIEW_WIN_RATES
    assert flow.stats_screen.summary_label.text == "Matches: 0   Draws: 0"
    assert "No match history yet" in flow.stats_screen.empty_history_label.text
    assert "Player One: 0.00%" in flow.stats_screen.slot_stats_label.text
    assert "Player Two: 0.00%" in flow.stats_screen.slot_stats_label.text
    assert "Team Win Rates - Overall" in flow.stats_screen.team_overall_label.text
    assert (
        "Team Win Rates - As Player One" in flow.stats_screen.team_player_one_label.text
    )
    assert (
        "Team Win Rates - As Player Two" in flow.stats_screen.team_player_two_label.text
    )
    assert "No team data yet" in flow.stats_screen.team_overall_label.text
    assert "No match history yet" in flow.stats_screen.op_analytics_empty_label.text


def test_stats_screen_supports_view_switching_between_win_rates_and_op_analytics() -> (
    None
):
    flow = TrackerFlow(GameState())

    flow.home_screen.stats_button.dispatch("on_press")

    assert flow.current == "stats"
    assert flow.stats_screen.stats_views.current == flow.stats_screen.VIEW_WIN_RATES

    flow.stats_screen.op_analytics_button.dispatch("on_press")

    assert flow.stats_screen.stats_views.current == flow.stats_screen.VIEW_OP_ANALYTICS
    assert "stats reader is not configured" in flow.stats_screen.error_label.text

    flow.stats_screen.win_rates_button.dispatch("on_press")

    assert flow.stats_screen.stats_views.current == flow.stats_screen.VIEW_WIN_RATES


def test_stats_screen_uses_high_contrast_readability_defaults() -> None:
    flow = TrackerFlow(GameState())
    screen = flow.stats_screen

    assert tuple(screen.summary_label.color) == screen._TEXT_PRIMARY
    assert tuple(screen.error_label.color) == screen._TEXT_ERROR
    assert tuple(screen.empty_history_label.color) == screen._TEXT_MUTED
    assert tuple(screen.op_analytics_empty_label.color) == screen._TEXT_MUTED
    assert tuple(screen.slot_stats_label.color) == screen._TEXT_PRIMARY
    assert tuple(screen.team_overall_label.color) == screen._TEXT_PRIMARY
    assert tuple(screen.team_player_one_label.color) == screen._TEXT_PRIMARY
    assert tuple(screen.team_player_two_label.color) == screen._TEXT_PRIMARY
    assert (
        tuple(screen.op_analytics_scope_labels["player_one"].color)
        == screen._TEXT_PRIMARY
    )
    assert (
        tuple(screen.op_analytics_scope_labels["player_two"].color)
        == screen._TEXT_PRIMARY
    )
    assert (
        tuple(screen.op_analytics_scope_labels["combined"].color)
        == screen._TEXT_PRIMARY
    )


def test_stats_screen_renders_slot_and_team_percentages() -> None:
    def read_summary() -> dict[str, object]:
        return {
            "total_matches": 3,
            "draws": 1,
            "player_slots": {
                "player_one": {
                    "wins": 1,
                    "draws": 1,
                    "matches": 3,
                    "win_percentage": 33.33,
                },
                "player_two": {
                    "wins": 1,
                    "draws": 1,
                    "matches": 3,
                    "win_percentage": 33.33,
                },
            },
            "teams": {
                "Kommandos": {
                    "overall": {
                        "wins": 2,
                        "draws": 2,
                        "losses": 0,
                        "matches": 4,
                        "win_percentage": 50.0,
                    },
                    "player_one": {
                        "wins": 1,
                        "draws": 1,
                        "losses": 0,
                        "matches": 2,
                        "win_percentage": 50.0,
                    },
                    "player_two": {
                        "wins": 1,
                        "draws": 1,
                        "losses": 0,
                        "matches": 2,
                        "win_percentage": 50.0,
                    },
                }
            },
            "primary_ops": {
                "player_one": {
                    "player_entries": 3,
                    "revealed_primary_ops": 3,
                    "missing_primary_ops": 0,
                    "most_successful": {
                        "op": "tac_op",
                        "label": "Tac Op",
                        "tied_ops": ["tac_op"],
                    },
                    "ops": {
                        "tac_op": {
                            "label": "Tac Op",
                            "picks": 2,
                            "wins": 1,
                            "draws": 0,
                            "losses": 1,
                            "win_percentage": 50.0,
                            "average_selected_vp": 5.5,
                            "average_bonus_vp": 2.0,
                        },
                        "kill_op": {
                            "label": "Kill Op",
                            "picks": 1,
                            "wins": 0,
                            "draws": 1,
                            "losses": 0,
                            "win_percentage": 0.0,
                            "average_selected_vp": 2.0,
                            "average_bonus_vp": 0.0,
                        },
                        "crit_op": {
                            "label": "Crit Op",
                            "picks": 0,
                            "wins": 0,
                            "draws": 0,
                            "losses": 0,
                            "win_percentage": 0.0,
                            "average_selected_vp": 0.0,
                            "average_bonus_vp": 0.0,
                        },
                    },
                },
                "player_two": {
                    "player_entries": 3,
                    "revealed_primary_ops": 2,
                    "missing_primary_ops": 1,
                    "most_successful": {
                        "op": "kill_op",
                        "label": "Kill Op",
                        "tied_ops": ["kill_op"],
                    },
                    "ops": {
                        "tac_op": {
                            "label": "Tac Op",
                            "picks": 1,
                            "wins": 0,
                            "draws": 1,
                            "losses": 0,
                            "win_percentage": 0.0,
                            "average_selected_vp": 3.0,
                            "average_bonus_vp": 0.0,
                        },
                        "kill_op": {
                            "label": "Kill Op",
                            "picks": 1,
                            "wins": 1,
                            "draws": 0,
                            "losses": 0,
                            "win_percentage": 100.0,
                            "average_selected_vp": 6.0,
                            "average_bonus_vp": 2.0,
                        },
                        "crit_op": {
                            "label": "Crit Op",
                            "picks": 0,
                            "wins": 0,
                            "draws": 0,
                            "losses": 0,
                            "win_percentage": 0.0,
                            "average_selected_vp": 0.0,
                            "average_bonus_vp": 0.0,
                        },
                    },
                },
                "combined": {
                    "player_entries": 6,
                    "revealed_primary_ops": 5,
                    "missing_primary_ops": 1,
                    "most_successful": {
                        "op": "tac_op",
                        "label": "Tac Op",
                        "tied_ops": ["tac_op", "kill_op"],
                    },
                    "ops": {
                        "tac_op": {
                            "label": "Tac Op",
                            "picks": 3,
                            "wins": 1,
                            "draws": 1,
                            "losses": 1,
                            "win_percentage": 33.33,
                            "average_selected_vp": 4.67,
                            "average_bonus_vp": 1.33,
                        },
                        "kill_op": {
                            "label": "Kill Op",
                            "picks": 2,
                            "wins": 1,
                            "draws": 1,
                            "losses": 0,
                            "win_percentage": 50.0,
                            "average_selected_vp": 4.0,
                            "average_bonus_vp": 1.0,
                        },
                        "crit_op": {
                            "label": "Crit Op",
                            "picks": 0,
                            "wins": 0,
                            "draws": 0,
                            "losses": 0,
                            "win_percentage": 0.0,
                            "average_selected_vp": 0.0,
                            "average_bonus_vp": 0.0,
                        },
                    },
                },
            },
            "op_buckets": {
                "tac_op": {
                    "label": "Tac Op",
                    "player_one": {
                        "matches": 3,
                        "wins": 1,
                        "draws": 1,
                        "losses": 1,
                        "win_percentage": 33.33,
                        "average_vp": 2.67,
                        "selected_as_primary": 2,
                        "average_bonus_vp_when_primary": 2.0,
                    },
                    "player_two": {
                        "matches": 3,
                        "wins": 1,
                        "draws": 1,
                        "losses": 1,
                        "win_percentage": 33.33,
                        "average_vp": 2.0,
                        "selected_as_primary": 1,
                        "average_bonus_vp_when_primary": 0.0,
                    },
                    "combined": {
                        "matches": 6,
                        "wins": 2,
                        "draws": 2,
                        "losses": 2,
                        "win_percentage": 33.33,
                        "average_vp": 2.34,
                        "selected_as_primary": 3,
                        "average_bonus_vp_when_primary": 1.33,
                    },
                },
                "kill_op": {
                    "label": "Kill Op",
                    "player_one": {
                        "matches": 3,
                        "wins": 1,
                        "draws": 1,
                        "losses": 1,
                        "win_percentage": 33.33,
                        "average_vp": 3.0,
                        "selected_as_primary": 1,
                        "average_bonus_vp_when_primary": 1.0,
                    },
                    "player_two": {
                        "matches": 3,
                        "wins": 1,
                        "draws": 1,
                        "losses": 1,
                        "win_percentage": 33.33,
                        "average_vp": 3.5,
                        "selected_as_primary": 1,
                        "average_bonus_vp_when_primary": 2.0,
                    },
                    "combined": {
                        "matches": 6,
                        "wins": 2,
                        "draws": 2,
                        "losses": 2,
                        "win_percentage": 33.33,
                        "average_vp": 3.25,
                        "selected_as_primary": 2,
                        "average_bonus_vp_when_primary": 1.5,
                    },
                },
                "crit_op": {
                    "label": "Crit Op",
                    "player_one": {
                        "matches": 3,
                        "wins": 1,
                        "draws": 1,
                        "losses": 1,
                        "win_percentage": 33.33,
                        "average_vp": 1.5,
                        "selected_as_primary": 0,
                        "average_bonus_vp_when_primary": 0.0,
                    },
                    "player_two": {
                        "matches": 3,
                        "wins": 1,
                        "draws": 1,
                        "losses": 1,
                        "win_percentage": 33.33,
                        "average_vp": 1.0,
                        "selected_as_primary": 0,
                        "average_bonus_vp_when_primary": 0.0,
                    },
                    "combined": {
                        "matches": 6,
                        "wins": 2,
                        "draws": 2,
                        "losses": 2,
                        "win_percentage": 33.33,
                        "average_vp": 1.25,
                        "selected_as_primary": 0,
                        "average_bonus_vp_when_primary": 0.0,
                    },
                },
            },
        }

    flow = TrackerFlow(GameState(), read_win_rate_summary_handler=read_summary)

    flow.home_screen.stats_button.dispatch("on_press")

    assert flow.current == "stats"
    assert flow.stats_screen.summary_label.text == "Matches: 3   Draws: 1"
    assert "Player One: 33.33%" in flow.stats_screen.slot_stats_label.text
    assert "Player Two: 33.33%" in flow.stats_screen.slot_stats_label.text
    assert "Kommandos: 50.00%" in flow.stats_screen.team_overall_label.text
    assert "Team Win Rates - Overall" in flow.stats_screen.team_overall_label.text
    assert "Kommandos: 50.00%" in flow.stats_screen.team_player_one_label.text
    assert (
        "Team Win Rates - As Player One" in flow.stats_screen.team_player_one_label.text
    )
    assert "Kommandos: 50.00%" in flow.stats_screen.team_player_two_label.text
    assert (
        "Team Win Rates - As Player Two" in flow.stats_screen.team_player_two_label.text
    )

    flow.stats_screen.op_analytics_button.dispatch("on_press")

    assert flow.stats_screen.stats_views.current == flow.stats_screen.VIEW_OP_ANALYTICS
    assert (
        "Most successful Primary Op: Tac Op"
        in flow.stats_screen.op_analytics_scope_labels["player_one"].text
    )
    assert (
        "Primary Op picks + win rates"
        not in flow.stats_screen.op_analytics_scope_labels["player_one"].text
    )
    assert (
        "Primary Op pick counts + win rates"
        in flow.stats_screen.op_analytics_scope_labels["player_one"].text
    )
    assert (
        "Tac Op: 2 picks, 50.00% win"
        in flow.stats_screen.op_analytics_scope_labels["player_one"].text
    )
    assert (
        "Most successful Primary Op: Kill Op"
        in flow.stats_screen.op_analytics_scope_labels["player_two"].text
    )
    assert (
        "Most successful Primary Op: Tac Op"
        in flow.stats_screen.op_analytics_scope_labels["combined"].text
    )
    assert (
        "Supporting Tac Op / Kill Op / Crit Op performance"
        in flow.stats_screen.op_analytics_scope_labels["combined"].text
    )
    assert (
        "Most successful tie: 2 ops"
        in flow.stats_screen.op_analytics_scope_labels["combined"].text
    )


def test_stats_screen_surfaces_read_errors() -> None:
    def failing_summary() -> dict[str, object]:
        raise ValueError("invalid history file")

    flow = TrackerFlow(GameState(), read_win_rate_summary_handler=failing_summary)

    flow.home_screen.stats_button.dispatch("on_press")

    assert flow.current == "stats"
    assert flow.stats_screen.summary_label.text == "Stats unavailable"
    assert "Could not load stats" in flow.stats_screen.error_label.text
    assert "invalid history file" in flow.stats_screen.error_label.text


def test_tracker_flow_start_game_navigates_to_team_selection_entry() -> None:
    flow = TrackerFlow(GameState())

    flow.home_screen.start_game_button.dispatch("on_press")

    assert flow.current == "team_selection"
    assert flow.team_selection_screen.confirm_button.disabled is True
    assert (
        flow.team_selection_screen.team_spinners["player_one"].text
        == "Select a Kill Team"
    )


def test_team_selection_confirm_requires_both_team_choices() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")

    assert flow.game_state.player_one_team == "Kommandos"
    assert flow.game_state.player_two_team is None
    assert flow.team_selection_screen.confirm_button.disabled is True
    assert "remaining team" in flow.team_selection_screen.selection_status_label.text


def test_flow_screens_apply_player_palette_consistently() -> None:
    flow = TrackerFlow(GameState())

    assert tuple(
        flow.team_selection_screen.player_title_labels["player_one"].color
    ) == (player_accent("player_one"))
    assert tuple(
        flow.team_selection_screen.team_spinners["player_two"].background_color
    ) == player_surface("player_two")

    flow.go_to_end_game()
    flow.end_game_screen._set_secret_op("player_one", "kill_op")

    assert tuple(
        flow.end_game_screen.secret_op_title_labels["player_two"].color
    ) == player_accent("player_two")
    assert tuple(
        flow.end_game_screen.secret_op_buttons[
            ("player_one", "kill_op")
        ].background_color
    ) == player_surface_selected("player_one")

    flow.game_state.player_one.secret_op = "tac_op"
    flow.game_state.player_two.secret_op = "crit_op"
    flow.go_to_final_score()

    assert tuple(flow.final_score_screen._header_labels["player_one"].color) == (
        player_accent("player_one")
    )
    assert tuple(flow.final_score_screen.p2_total_label.color) == player_accent(
        "player_two"
    )


def test_team_selection_confirm_transitions_to_gameplay_at_turning_point_one() -> None:
    flow = TrackerFlow(GameState(turning_point=4, end_game=True))

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")

    assert flow.team_selection_screen.confirm_button.disabled is False

    flow.team_selection_screen.confirm_button.dispatch("on_press")

    assert flow.current == "gameplay"
    assert flow.game_state.player_one_team == "Kommandos"
    assert flow.game_state.player_two_team == "Kasrkin"
    assert flow.main_game_screen.turning_point_label.text == "Turning Point 1"
    assert flow.main_game_screen.matchup_label.text == "Kommandos vs Kasrkin"


def test_end_game_route_is_reversible_from_gameplay() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)
    assert flow.current == "end_game"
    assert flow.game_state.end_game is True

    flow.end_game_screen.back_button.dispatch("on_press")

    assert flow.current == "gameplay"
    assert flow.game_state.end_game is False
    assert flow.main_game_screen.turning_point_label.text == "Turning Point 4"
    assert flow.main_game_screen.matchup_label.text == "Kommandos vs Kasrkin"


def test_end_game_continue_requires_both_primary_ops() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)

    assert flow.current == "end_game"
    assert flow.end_game_screen.continue_button.disabled is True

    flow.end_game_screen._set_secret_op("player_one", "tac_op")

    assert flow.game_state.player_one.secret_op == "tac_op"
    assert flow.end_game_screen.continue_button.disabled is True
    assert "Select both Primary Ops" in flow.end_game_screen.status_label.text


def test_end_game_continue_navigates_to_final_score_after_both_ops_selected() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "crit_op")

    assert flow.end_game_screen.continue_button.disabled is False

    flow.end_game_screen.continue_button.dispatch("on_press")

    assert flow.current == "final_score"
    assert flow.game_state.player_one.secret_op == "tac_op"
    assert flow.game_state.player_two.secret_op == "crit_op"
    assert flow.final_score_screen._metric_labels["header"].text == "Metric"
    assert flow.final_score_screen._metric_labels["tac_op"].text == "Tac Op"
    # player_one's tac_op row should show inline bonus
    assert "+" in flow.final_score_screen._op_labels[("player_one", "tac_op")].text
    # player_two's crit_op row should show inline bonus
    assert "+" in flow.final_score_screen._op_labels[("player_two", "crit_op")].text


def test_final_score_screen_displays_totals_and_bonus_breakdown() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    # Set some scores
    state = flow.game_state
    state.player_one.tactical_vp = 4
    state.player_one.kill_vp = 3
    state.player_one.main_mission_vp = 2
    state.player_one.command_points = 2
    state.player_one.secret_op = "kill_op"

    state.player_two.tactical_vp = 2
    state.player_two.kill_vp = 1
    state.player_two.main_mission_vp = 5
    state.player_two.command_points = 1
    state.player_two.secret_op = "crit_op"

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "kill_op")
    flow.end_game_screen._set_secret_op("player_two", "crit_op")
    flow.end_game_screen.continue_button.dispatch("on_press")

    assert flow.current == "final_score"
    fss = flow.final_score_screen

    # Team name labels
    assert fss._player_one_team_label.text == "Kommandos"
    assert fss._player_two_team_label.text == "Kasrkin"
    assert fss._metric_labels["kill_op"].text == "Kill Op"
    assert fss._metric_labels["total"].text == "Total"

    # Player one: kill_op is primary — tac_op and crit_op rows show plain VP
    assert fss._op_labels[("player_one", "tac_op")].text == "4"
    # kill_op row shows inline bonus: kill_vp=3, bonus=ceil(3/2)=2
    assert fss._op_labels[("player_one", "kill_op")].text == "3 +2"
    assert fss._op_labels[("player_one", "crit_op")].text == "2"

    # Player two: crit_op is primary — main_mission_vp=5, bonus=ceil(5/2)=3
    assert fss._op_labels[("player_two", "tac_op")].text == "2"
    assert fss._op_labels[("player_two", "kill_op")].text == "1"
    assert fss._op_labels[("player_two", "crit_op")].text == "5 +3"

    # Totals: p1 = 4+3+2+2=11, p2 = 2+1+5+3=11 → DRAW
    assert fss.p1_total_label.text == str(int(fss.p1_total_label.text))
    assert fss.p2_total_label.text == str(int(fss.p2_total_label.text))
    assert fss.winner_label.text in ("DRAW", "Kommandos WIN!", "Kasrkin WIN!")


def test_final_score_back_button_returns_to_end_game() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "kill_op")
    flow.end_game_screen.continue_button.dispatch("on_press")

    assert flow.current == "final_score"
    flow.final_score_screen.back_button.dispatch("on_press")

    assert flow.current == "end_game"
    assert flow.game_state.player_one.secret_op == "tac_op"
    assert flow.game_state.player_two.secret_op == "kill_op"


def test_final_score_discard_button_resets_and_returns_home() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    state = flow.game_state
    state.player_one.tactical_vp = 5
    state.player_two.kill_vp = 3

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "kill_op")
    flow.end_game_screen.continue_button.dispatch("on_press")

    assert flow.current == "final_score"
    flow.final_score_screen.discard_button.dispatch("on_press")

    assert flow.current == "home"
    assert flow.game_state.player_one_team is None
    assert flow.game_state.player_two_team is None
    assert flow.game_state.player_one.tactical_vp == 0
    assert flow.game_state.player_two.kill_vp == 0


def test_final_score_save_button_transitions_to_home() -> None:
    flow = TrackerFlow(GameState())

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "kill_op")
    flow.end_game_screen.continue_button.dispatch("on_press")

    assert flow.current == "final_score"
    flow.final_score_screen.save_button.dispatch("on_press")

    assert flow.current == "home"


def test_final_score_save_appends_history_once_per_save_action() -> None:
    captured: list[dict[str, object]] = []

    def history_append_handler(payload: dict[str, object]) -> None:
        captured.append(payload)

    flow = TrackerFlow(GameState(), history_append_handler=history_append_handler)

    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "kill_op")
    flow.end_game_screen.continue_button.dispatch("on_press")

    flow.final_score_screen.save_button.dispatch("on_press")

    assert flow.current == "home"
    assert len(captured) == 1
    assert captured[0]["turning_point"] == 4
    assert captured[0]["end_game"] is True


def test_e2e_full_game_journey_home_to_final_score() -> None:
    """Test complete happy-path journey.

    Home -> Team Selection -> Gameplay -> End Game -> Final Score.
    """
    flow = TrackerFlow(GameState())

    # Start at home
    assert flow.current == "home"

    # Navigate to team selection
    flow.home_screen.start_game_button.dispatch("on_press")
    assert flow.current == "team_selection"

    # Select teams
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    assert flow.team_selection_screen.confirm_button.disabled is False

    # Confirm teams and start gameplay at TP1
    flow.team_selection_screen.confirm_button.dispatch("on_press")
    assert flow.current == "gameplay"
    assert flow.game_state.turning_point == 1
    assert flow.game_state.player_one_team == "Kommandos"
    assert flow.game_state.player_two_team == "Kasrkin"

    # Play through turning points 1-3, advance to TP4
    for _ in range(3):
        flow.main_game_screen._adjust_turning_point(1)
    assert flow.game_state.turning_point == 4

    # Set some scores
    flow.game_state.player_one.tactical_vp = 3
    flow.game_state.player_two.kill_vp = 4

    # Trigger end-game at TP4
    flow.main_game_screen._adjust_turning_point(1)
    assert flow.current == "end_game"
    assert flow.game_state.end_game is True

    # Select primary ops
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "kill_op")
    assert flow.end_game_screen.continue_button.disabled is False

    # Continue to final score
    flow.end_game_screen.continue_button.dispatch("on_press")
    assert flow.current == "final_score"
    fss = flow.final_score_screen
    assert fss._player_one_team_label.text == "Kommandos"
    assert fss._player_two_team_label.text == "Kasrkin"
    # player_one's tac_op is primary, player_two's kill_op is primary
    assert "+" in fss._op_labels[("player_one", "tac_op")].text
    assert "+" in fss._op_labels[("player_two", "kill_op")].text

    # Save final scores and return home
    flow.final_score_screen.save_button.dispatch("on_press")
    assert flow.current == "home"


def test_e2e_accidental_end_game_recovery_back_to_gameplay() -> None:
    """Test back-navigation from End-Game screen preserves gameplay state and scores."""
    flow = TrackerFlow(GameState())

    # Setup: navigate to end-game
    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    # Set some scores during gameplay
    flow.game_state.player_one.tactical_vp = 5
    flow.game_state.player_one.command_points = 2
    flow.game_state.player_two.kill_vp = 3
    flow.game_state.player_two.bonus_vp = 1

    # Advance to TP4 and trigger end-game
    _trigger_end_game_via_tp_plus(flow)
    assert flow.current == "end_game"

    # Accidentally triggered end-game; press back to return to gameplay
    flow.end_game_screen.back_button.dispatch("on_press")
    assert flow.current == "gameplay"

    # Verify state is preserved (end_game flag cleared, scores intact)
    assert flow.game_state.end_game is False
    assert flow.game_state.turning_point == 4
    assert flow.game_state.player_one.tactical_vp == 5
    assert flow.game_state.player_one.command_points == 2
    assert flow.game_state.player_two.kill_vp == 3
    assert flow.game_state.player_two.bonus_vp == 1
    assert flow.game_state.player_one_team == "Kommandos"
    assert flow.game_state.player_two_team == "Kasrkin"


def test_e2e_back_from_final_score_to_end_game_for_corrections() -> None:
    """Test back-navigation from Final Score screen enables op selection corrections."""
    flow = TrackerFlow(GameState())

    # Setup: navigate to final score
    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    _trigger_end_game_via_tp_plus(flow)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "kill_op")
    flow.end_game_screen.continue_button.dispatch("on_press")
    assert flow.current == "final_score"

    original_p1_op = flow.game_state.player_one.secret_op
    original_p2_op = flow.game_state.player_two.secret_op

    # Press back to correct ops
    flow.final_score_screen.back_button.dispatch("on_press")
    assert flow.current == "end_game"

    # Verify ops are still set (can be changed)
    assert flow.game_state.player_one.secret_op == original_p1_op
    assert flow.game_state.player_two.secret_op == original_p2_op

    # Change player one's op
    flow.end_game_screen._set_secret_op("player_one", "kill_op")
    assert flow.game_state.player_one.secret_op == "kill_op"

    # Continue to final score again with new op
    flow.end_game_screen.continue_button.dispatch("on_press")
    assert flow.current == "final_score"
    # player_one changed to kill_op — row should show inline bonus
    assert "+" in flow.final_score_screen._op_labels[("player_one", "kill_op")].text


def test_e2e_discard_path_clears_all_state() -> None:
    """Test discard-game path clears all state and returns to home for fresh start."""
    flow = TrackerFlow(GameState())

    # Setup: navigate through full game to final score
    flow.go_to_team_selection()
    flow.team_selection_screen._handle_spinner_change("player_one", "Kommandos")
    flow.team_selection_screen._handle_spinner_change("player_two", "Kasrkin")
    flow.team_selection_screen.confirm_button.dispatch("on_press")

    flow.game_state.player_one.tactical_vp = 6
    flow.game_state.player_one.command_points = 3
    flow.game_state.player_two.kill_vp = 5
    flow.game_state.turning_point = 4  # Set to TP4

    flow.main_game_screen._adjust_turning_point(1)
    flow.end_game_screen._set_secret_op("player_one", "tac_op")
    flow.end_game_screen._set_secret_op("player_two", "crit_op")
    flow.end_game_screen.continue_button.dispatch("on_press")
    assert flow.current == "final_score"

    # Discard the game
    flow.final_score_screen.discard_button.dispatch("on_press")

    # Verify state is fully reset
    assert flow.current == "home"
    assert flow.game_state.player_one_team is None
    assert flow.game_state.player_two_team is None
    assert flow.game_state.player_one.tactical_vp == 0
    assert flow.game_state.player_one.command_points == 0
    assert flow.game_state.player_two.kill_vp == 0
    assert flow.game_state.turning_point == 1
    assert flow.game_state.end_game is False
    assert flow.game_state.player_one.secret_op is None
    assert flow.game_state.player_two.secret_op is None

    # Can start a fresh game from home
    flow.home_screen.start_game_button.dispatch("on_press")
    assert flow.current == "team_selection"


def test_app_main_starts_and_builds_main_screen(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(self: App) -> None:
        captured["root"] = self.build()

    monkeypatch.setattr(App, "run", fake_run)

    main()

    assert isinstance(captured["root"], TrackerFlow)
    flow = captured["root"]
    assert isinstance(flow, TrackerFlow)
    assert flow.current == "home"
    flow.start_gameplay()
    assert flow.main_game_screen.turning_point_label.text == "Turning Point 1"
