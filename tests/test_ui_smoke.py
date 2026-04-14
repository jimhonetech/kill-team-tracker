"""Low-maintenance UI smoke tests for app startup and screen loading."""

from __future__ import annotations

from kivy.app import App

from app.main import main
from app.state import GameState
from app.ui.main_screen import MainGameScreen


def test_main_game_screen_loads_with_default_state() -> None:
    screen = MainGameScreen(GameState())

    assert screen.title_label.text == "Kill Team Tracker"
    assert screen.turning_point_label.text == "Turning Point 1"
    assert not hasattr(screen, "operation_label")
    assert not hasattr(screen, "operation_controls")
    assert screen.end_game_controls.height == 0
    assert screen.total_value_labels["player_one"].text == "0"
    assert screen.total_value_labels["player_two"].text == "0"


def test_app_main_starts_and_builds_main_screen(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(self: App) -> None:
        captured["root"] = self.build()

    monkeypatch.setattr(App, "run", fake_run)

    main()

    assert isinstance(captured["root"], MainGameScreen)
    screen = captured["root"]
    assert isinstance(screen, MainGameScreen)
    assert screen.turning_point_label.text == "Turning Point 1"
