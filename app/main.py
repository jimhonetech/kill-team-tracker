#!/usr/bin/env python3
"""Kill Team Tracker application entry point for UI startup."""

from __future__ import annotations


def main() -> None:
    try:
        from kivy.app import App
    except ModuleNotFoundError:
        print(
            "Kivy is not installed. Complete packaging/setup tasks before running UI."
        )
        return

    from app.state import GameState
    from app.ui import MainGameScreen

    class KillTeamTrackerApp(App):
        def build(self) -> MainGameScreen:
            return MainGameScreen(game_state=GameState())

    KillTeamTrackerApp().run()


if __name__ == "__main__":
    main()
