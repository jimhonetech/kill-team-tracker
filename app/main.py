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
    from app.storage.adapter import StorageAdapter
    from app.ui import MainGameScreen

    storage_adapter = StorageAdapter()

    class KillTeamTrackerApp(App):
        def build(self) -> MainGameScreen:
            return MainGameScreen(
                game_state=GameState(),
                save_handler=storage_adapter.save_handler,
                resume_handler=storage_adapter.resume_handler,
            )

    KillTeamTrackerApp().run()


if __name__ == "__main__":
    main()
