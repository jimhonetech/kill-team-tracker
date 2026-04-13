"""Main game screen for Kill Team Tracker V1."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from app.state import GameState


class MainGameScreen(BoxLayout):
    """Main screen with turning point and both players' core score sections."""

    SCORE_ROWS = (
        ("Command Points", "cp", None),
        ("Tactical VP", "vp", "tactical_vp"),
        ("Kill VP", "vp", "kill_vp"),
        ("Main VP", "vp", "main_mission_vp"),
    )

    def __init__(self, game_state: GameState, **kwargs: object) -> None:
        super().__init__(orientation="vertical", spacing=16, padding=24, **kwargs)
        self.game_state = game_state
        self.score_value_labels: dict[tuple[str, str], Label] = {}

        self.title_label = Label(
            text="Kill Team Tracker",
            font_size="28sp",
            size_hint=(1, 0.1),
        )
        self.turning_point_label = Label(
            text="",
            font_size="32sp",
            bold=True,
            size_hint=(1, 0.1),
        )

        self.player_sections = BoxLayout(
            orientation="horizontal",
            spacing=16,
            size_hint=(1, 0.8),
        )

        self.player_sections.add_widget(
            self._build_player_panel("player_one", "Player One")
        )
        self.player_sections.add_widget(
            self._build_player_panel("player_two", "Player Two")
        )

        self.add_widget(self.title_label)
        self.add_widget(self.turning_point_label)
        self.add_widget(self.player_sections)
        self.refresh_from_state()

    def _build_player_panel(self, player: str, title: str) -> BoxLayout:
        panel = BoxLayout(orientation="vertical", spacing=8)
        panel.add_widget(Label(text=title, font_size="22sp", size_hint=(1, 0.2)))

        for row_title, row_type, category in self.SCORE_ROWS:
            panel.add_widget(
                self._build_score_row(player, row_title, row_type, category)
            )

        return panel

    def _build_score_row(
        self,
        player: str,
        row_title: str,
        row_type: str,
        category: str | None,
    ) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.2))
        row.add_widget(Label(text=row_title, halign="left", size_hint=(0.5, 1)))

        minus_button = Button(text="-", size_hint=(0.15, 1))
        value_label = Label(text="0", size_hint=(0.2, 1))
        plus_button = Button(text="+", size_hint=(0.15, 1))

        key = category if category is not None else "command_points"
        self.score_value_labels[(player, key)] = value_label

        if row_type == "cp":
            minus_button.bind(on_press=lambda _instance: self._adjust_cp(player, -1))
            plus_button.bind(on_press=lambda _instance: self._adjust_cp(player, 1))
        else:
            assert category is not None
            minus_button.bind(
                on_press=lambda _instance: self._adjust_vp(player, category, -1)
            )
            plus_button.bind(
                on_press=lambda _instance: self._adjust_vp(player, category, 1)
            )

        row.add_widget(minus_button)
        row.add_widget(value_label)
        row.add_widget(plus_button)
        return row

    def _adjust_cp(self, player: str, direction: int) -> None:
        if direction > 0:
            self.game_state.increment_command_points(player)
        else:
            self.game_state.decrement_command_points(player)
        self.refresh_from_state()

    def _adjust_vp(self, player: str, category: str, direction: int) -> None:
        if direction > 0:
            self.game_state.increment_vp(player, category)
        else:
            self.game_state.decrement_vp(player, category)
        self.refresh_from_state()

    def refresh_from_state(self) -> None:
        self.turning_point_label.text = f"Turning Point {self.game_state.turning_point}"
        for player in ("player_one", "player_two"):
            scores = self.game_state._get_player_scores(player)
            self.score_value_labels[(player, "command_points")].text = str(
                scores.command_points
            )
            self.score_value_labels[(player, "tactical_vp")].text = str(
                scores.tactical_vp
            )
            self.score_value_labels[(player, "kill_vp")].text = str(scores.kill_vp)
            self.score_value_labels[(player, "main_mission_vp")].text = str(
                scores.main_mission_vp
            )
