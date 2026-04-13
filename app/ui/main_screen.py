"""Main game screen for Kill Team Tracker V1."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.state import GameState


class MainGameScreen(BoxLayout):
    """Simple main screen that displays the active turning point."""

    def __init__(self, game_state: GameState, **kwargs: object) -> None:
        super().__init__(orientation="vertical", spacing=16, padding=24, **kwargs)
        self.game_state = game_state

        self.title_label = Label(
            text="Kill Team Tracker",
            font_size="28sp",
            size_hint=(1, 0.25),
        )
        self.turning_point_label = Label(
            text="",
            font_size="44sp",
            bold=True,
            size_hint=(1, 0.75),
        )

        self.add_widget(self.title_label)
        self.add_widget(self.turning_point_label)
        self.refresh_from_state()

    def refresh_from_state(self) -> None:
        self.turning_point_label.text = f"Turning Point {self.game_state.turning_point}"
