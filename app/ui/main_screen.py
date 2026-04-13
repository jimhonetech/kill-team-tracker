"""Main game screen for Kill Team Tracker V1."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from app.state import GameState


class MainGameScreen(BoxLayout):
    """Main screen with turning point and both players' core score sections."""

    OPERATIONS = ("Secure Objective", "Infiltration", "Recon Sweep")
    SCORE_ROWS = (
        ("Command Points", "cp", None),
        ("Tactical VP", "vp", "tactical_vp"),
        ("Kill VP", "vp", "kill_vp"),
        ("Main VP", "vp", "main_mission_vp"),
    )

    def __init__(self, game_state: GameState, **kwargs: object) -> None:
        save_handler = cast(
            Callable[[dict[str, object]], None] | None,
            kwargs.pop("save_handler", None),
        )
        resume_handler = cast(
            Callable[[], dict[str, object]] | None,
            kwargs.pop("resume_handler", None),
        )
        super().__init__(orientation="vertical", spacing=16, padding=24, **kwargs)
        self.game_state = game_state
        self.save_handler: Callable[[dict[str, object]], None] | None = save_handler
        self.resume_handler: Callable[[], dict[str, object]] | None = resume_handler
        self.reset_pending = False
        self.score_value_labels: dict[tuple[str, str], Label] = {}
        self.total_value_labels: dict[str, Label] = {}
        self.bonus_buttons: dict[str, tuple[Button, Button]] = {}

        self.title_label = Label(
            text="Kill Team Tracker",
            font_size="28sp",
            size_hint=(1, 0.1),
        )
        self.turning_point_label = Label(
            text="",
            font_size="32sp",
            bold=True,
            size_hint=(1, 0.08),
        )

        self.operation_label = Label(
            text="",
            font_size="20sp",
            size_hint=(1, 0.06),
        )

        self.operation_controls = self._build_operation_controls()
        self.persistence_controls = self._build_persistence_controls()
        self.reset_controls = self._build_reset_controls()

        self.player_sections = BoxLayout(
            orientation="horizontal",
            spacing=16,
            size_hint=(1, 0.70),
        )

        self.player_sections.add_widget(
            self._build_player_panel("player_one", "Player One")
        )
        self.player_sections.add_widget(
            self._build_player_panel("player_two", "Player Two")
        )

        self.add_widget(self.title_label)
        self.add_widget(self.turning_point_label)
        self.add_widget(self.operation_label)
        self.add_widget(self.operation_controls)
        self.add_widget(self.persistence_controls)
        self.add_widget(self.reset_controls)
        self.add_widget(self.player_sections)
        self.refresh_from_state()

    def _build_operation_controls(self) -> BoxLayout:
        controls = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.06))
        controls.add_widget(
            Button(
                text="No Operation",
                on_press=lambda _instance: self._set_operation(None),
            )
        )
        for operation in self.OPERATIONS:
            controls.add_widget(
                Button(
                    text=operation,
                    on_press=lambda _instance, op=operation: self._set_operation(op),
                )
            )
        return controls

    def _build_persistence_controls(self) -> BoxLayout:
        controls = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.06))
        self.persistence_status_label = Label(text="", size_hint=(0.45, 1))
        self.save_button = Button(
            text="Save",
            size_hint=(0.275, 1),
            on_press=lambda _instance: self._save_game(),
        )
        self.resume_button = Button(
            text="Resume",
            size_hint=(0.275, 1),
            on_press=lambda _instance: self._resume_game(),
        )

        controls.add_widget(self.persistence_status_label)
        controls.add_widget(self.save_button)
        controls.add_widget(self.resume_button)
        return controls

    def _build_reset_controls(self) -> BoxLayout:
        controls = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.06))
        self.reset_status_label = Label(text="", size_hint=(0.45, 1))
        self.reset_button = Button(
            text="New Game",
            size_hint=(0.2, 1),
            on_press=lambda _instance: self._request_reset(),
        )
        self.reset_confirm_button = Button(
            text="Confirm",
            size_hint=(0.175, 1),
            disabled=True,
            on_press=lambda _instance: self._confirm_reset(),
        )
        self.reset_cancel_button = Button(
            text="Cancel",
            size_hint=(0.175, 1),
            disabled=True,
            on_press=lambda _instance: self._cancel_reset(),
        )

        controls.add_widget(self.reset_status_label)
        controls.add_widget(self.reset_button)
        controls.add_widget(self.reset_confirm_button)
        controls.add_widget(self.reset_cancel_button)
        return controls

    def _build_player_panel(self, player: str, title: str) -> BoxLayout:
        panel = BoxLayout(orientation="vertical", spacing=8)
        panel.add_widget(Label(text=title, font_size="22sp", size_hint=(1, 0.18)))

        for row_title, row_type, category in self.SCORE_ROWS:
            panel.add_widget(
                self._build_score_row(player, row_title, row_type, category)
            )

        panel.add_widget(self._build_bonus_row(player))
        panel.add_widget(self._build_total_row(player))

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

    def _build_bonus_row(self, player: str) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.16))
        row.add_widget(Label(text="Bonus VP", halign="left", size_hint=(0.5, 1)))

        minus_button = Button(text="-", size_hint=(0.15, 1))
        value_label = Label(text="0", size_hint=(0.2, 1))
        plus_button = Button(text="+", size_hint=(0.15, 1))

        self.score_value_labels[(player, "bonus_vp")] = value_label
        self.bonus_buttons[player] = (minus_button, plus_button)

        minus_button.bind(on_press=lambda _instance: self._adjust_bonus(player, -1))
        plus_button.bind(on_press=lambda _instance: self._adjust_bonus(player, 1))

        row.add_widget(minus_button)
        row.add_widget(value_label)
        row.add_widget(plus_button)
        return row

    def _build_total_row(self, player: str) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.16))
        row.add_widget(Label(text="Total VP", halign="left", size_hint=(0.6, 1)))
        total_label = Label(text="0", size_hint=(0.4, 1))
        self.total_value_labels[player] = total_label
        row.add_widget(total_label)
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

    def _set_operation(self, operation: str | None) -> None:
        self.game_state.select_operation(operation)
        if operation is None:
            self.game_state.set_bonus_vp("player_one", 0)
            self.game_state.set_bonus_vp("player_two", 0)
        self.refresh_from_state()

    def _adjust_bonus(self, player: str, direction: int) -> None:
        if self.game_state.selected_operation is None:
            return

        scores = self.game_state._get_player_scores(player)
        next_points = scores.bonus_vp + direction
        self.game_state.set_bonus_vp(player, next_points)
        self.refresh_from_state()

    def _request_reset(self) -> None:
        self.reset_pending = True
        self.refresh_from_state()

    def _confirm_reset(self) -> None:
        if not self.reset_pending:
            return
        self.game_state.reset_game()
        self.reset_pending = False
        self.refresh_from_state()

    def _cancel_reset(self) -> None:
        self.reset_pending = False
        self.refresh_from_state()

    def _save_game(self) -> None:
        if self.save_handler is None:
            self.persistence_status_label.text = "Save unavailable"
            return

        try:
            self.save_handler(self.game_state.to_dict())
            self.persistence_status_label.text = "Game saved"
        except Exception as exc:  # noqa: BLE001
            self.persistence_status_label.text = f"Save failed: {exc}"

    def _resume_game(self) -> None:
        if self.resume_handler is None:
            self.persistence_status_label.text = "Resume unavailable"
            return

        try:
            payload = self.resume_handler()
            self.game_state = GameState.from_dict(payload)
            self.reset_pending = False
            self.refresh_from_state()
            self.persistence_status_label.text = "Game resumed"
        except Exception as exc:  # noqa: BLE001
            self.persistence_status_label.text = f"Resume failed: {exc}"

    def refresh_from_state(self) -> None:
        self.turning_point_label.text = f"Turning Point {self.game_state.turning_point}"
        selected = self.game_state.selected_operation or "None"
        self.operation_label.text = f"Operation: {selected}"

        bonus_enabled = self.game_state.selected_operation is not None
        for minus_button, plus_button in self.bonus_buttons.values():
            minus_button.disabled = not bonus_enabled
            plus_button.disabled = not bonus_enabled

        self.reset_confirm_button.disabled = not self.reset_pending
        self.reset_cancel_button.disabled = not self.reset_pending
        self.reset_status_label.text = "Confirm reset?" if self.reset_pending else ""

        totals = self.game_state.final_scores()
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
            self.score_value_labels[(player, "bonus_vp")].text = str(scores.bonus_vp)
            self.total_value_labels[player].text = str(totals[player])
