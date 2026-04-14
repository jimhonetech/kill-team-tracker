"""Main game screen for Kill Team Tracker V1."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import cast

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from app.state import GameState
from app.state.models import TURN_MAX, TURN_MIN
from app.ui.player_palette import (
    player_accent,
    player_button_text,
    player_surface,
    player_surface_selected,
)


class MainGameScreen(BoxLayout):
    """Focused gameplay screen with in-match score tracking and TP4 end-game entry."""

    SECRET_OPS = (
        ("Tac Op", "tac_op"),
        ("Kill Op", "kill_op"),
        ("Crit Op", "crit_op"),
    )
    SECRET_OP_LABELS = {op: label for label, op in SECRET_OPS}
    SUMMARY_PRIMARY_MARKER = "[PRIMARY]"
    SCORE_ROWS = (
        ("Command Points", "cp", None),
        ("Tac Op", "vp", "tactical_vp"),
        ("Kill Op", "vp", "kill_vp"),
        ("Crit Op", "vp", "main_mission_vp"),
    )

    def __init__(self, game_state: GameState, **kwargs: object) -> None:
        end_game_handler = cast(
            Callable[[], None] | None, kwargs.pop("end_game_handler", None)
        )
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
        self.end_game_handler: Callable[[], None] | None = end_game_handler
        self.save_handler: Callable[[dict[str, object]], None] | None = save_handler
        self.resume_handler: Callable[[], dict[str, object]] | None = resume_handler
        self.reset_pending = False
        self.score_value_labels: dict[tuple[str, str], Label] = {}
        self.score_title_labels: dict[tuple[str, str], Label] = {}
        self.total_value_labels: dict[str, Label] = {}
        self.total_title_labels: dict[str, Label] = {}
        self.secret_op_buttons: dict[tuple[str, str], Button] = {}
        self.secret_op_status_labels: dict[str, Label] = {}
        self.player_title_labels: dict[str, Label] = {}
        self.secret_op_title_labels: dict[str, Label] = {}
        self.summary_player_labels: dict[str, Label] = {}

        self.title_label = Label(text="Gameplay", font_size="28sp", size_hint=(1, 0.1))
        self.matchup_label = Label(text="", font_size="18sp", size_hint=(1, 0.06))
        self.turning_point_controls = self._build_turning_point_controls()
        self.end_game_controls = self._build_end_game_controls()
        self.end_game_summary = self._build_end_game_summary()
        self.persistence_controls = self._build_persistence_controls()
        self.reset_controls = self._build_reset_controls()

        self.player_sections = BoxLayout(
            orientation="horizontal", spacing=16, size_hint=(1, 0.86)
        )

        self.player_sections.add_widget(
            self._build_player_panel("player_one", "Player One")
        )
        self.player_sections.add_widget(
            self._build_player_panel("player_two", "Player Two")
        )

        self.add_widget(self.title_label)
        self.add_widget(self.matchup_label)
        self.add_widget(self.turning_point_controls)
        self.add_widget(self.player_sections)
        self.refresh_from_state()

    def _build_turning_point_controls(self) -> BoxLayout:
        controls = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.08))
        self.turning_point_decrement_button = Button(
            text="-",
            size_hint=(0.2, 1),
            on_press=lambda _instance: self._adjust_turning_point(-1),
        )
        self.tp_minus_button = self.turning_point_decrement_button
        self.turning_point_label = Label(
            text="",
            font_size="32sp",
            bold=True,
            size_hint=(0.6, 1),
        )
        self.turning_point_increment_button = Button(
            text="+",
            size_hint=(0.2, 1),
            on_press=lambda _instance: self._adjust_turning_point(1),
        )
        self.tp_plus_button = self.turning_point_increment_button

        controls.add_widget(self.turning_point_decrement_button)
        controls.add_widget(self.turning_point_label)
        controls.add_widget(self.turning_point_increment_button)
        return controls

    def _build_end_game_controls(self) -> BoxLayout:
        controls = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint=(1, None),
            height=0,
            opacity=0,
        )
        controls.add_widget(
            Label(
                text="End Game",
                font_size="20sp",
                bold=True,
                size_hint=(1, None),
                height=32,
            )
        )

        player_controls = BoxLayout(orientation="horizontal", spacing=16)
        player_controls.add_widget(
            self._build_secret_op_panel("player_one", "Player 1")
        )
        player_controls.add_widget(
            self._build_secret_op_panel("player_two", "Player 2")
        )
        controls.add_widget(player_controls)
        return controls

    def _build_secret_op_panel(self, player: str, title: str) -> BoxLayout:
        panel = BoxLayout(orientation="vertical", spacing=8)
        title_label = Label(
            text=title,
            font_size="18sp",
            size_hint=(1, None),
            height=28,
            color=player_accent(player),
        )
        self.secret_op_title_labels[player] = title_label
        panel.add_widget(title_label)

        button_row = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint=(1, None),
            height=44,
        )
        for label, op in self.SECRET_OPS:
            button = Button(
                text=label,
                background_normal="",
                background_down="",
                background_color=player_surface(player),
                color=player_button_text(False),
            )
            button.bind(on_press=partial(self._handle_secret_op_press, player, op))
            self.secret_op_buttons[(player, op)] = button
            button_row.add_widget(button)

        status_label = Label(
            text="Selected: None",
            size_hint=(1, None),
            height=24,
            color=player_accent(player),
        )
        self.secret_op_status_labels[player] = status_label

        panel.add_widget(button_row)
        panel.add_widget(status_label)
        return panel

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

    def _build_end_game_summary(self) -> BoxLayout:
        summary = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint=(1, None),
            height=0,
            opacity=0,
        )
        summary.add_widget(
            Label(
                text="End-Game Summary",
                font_size="20sp",
                bold=True,
                size_hint=(1, None),
                height=32,
            )
        )

        content = BoxLayout(orientation="horizontal", spacing=16)
        content.add_widget(self._build_summary_player_panel("player_one", "Player One"))
        content.add_widget(self._build_summary_player_panel("player_two", "Player Two"))
        summary.add_widget(content)
        return summary

    def _build_summary_player_panel(self, player: str, title: str) -> Label:
        label = Label(
            text=title,
            halign="left",
            valign="top",
            color=player_accent(player),
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.summary_player_labels[player] = label
        return label

    def _format_summary_op_line(
        self, op: str, value: int, primary_op: str | None
    ) -> str:
        marker = f" {self.SUMMARY_PRIMARY_MARKER}" if primary_op == op else ""
        return f"{self.SECRET_OP_LABELS[op]}: {value} VP{marker}"

    def _format_player_summary(self, player: str, heading: str) -> str:
        scores = self.game_state._get_player_scores(player)
        primary_op = scores.secret_op
        primary_label = (
            self.SECRET_OP_LABELS[primary_op] if primary_op is not None else "None"
        )

        tac_line = self._format_summary_op_line(
            "tac_op", scores.tactical_vp, primary_op
        )
        kill_line = self._format_summary_op_line("kill_op", scores.kill_vp, primary_op)
        crit_line = self._format_summary_op_line(
            "crit_op", scores.main_mission_vp, primary_op
        )

        primary_vp = 0
        if primary_op == "tac_op":
            primary_vp = scores.tactical_vp
        elif primary_op == "kill_op":
            primary_vp = scores.kill_vp
        elif primary_op == "crit_op":
            primary_vp = scores.main_mission_vp

        bonus = self.game_state.calculate_bonus_vp(player)
        tracked_bonus = scores.bonus_vp
        base_vp_sum = scores.tactical_vp + scores.kill_vp + scores.main_mission_vp
        formula_total = base_vp_sum + bonus
        tracked_total = base_vp_sum + tracked_bonus

        return "\n".join(
            (
                heading,
                tac_line,
                kill_line,
                crit_line,
                (
                    "Primary Op: "
                    f"{primary_label} ({primary_vp} VP) -> "
                    "Formula Bonus: "
                    f"{bonus} (calculate_bonus_vp = ceil({primary_vp}/2))"
                ),
                f"Formula Total: {base_vp_sum} + {bonus} = {formula_total}",
                f"Tracked Total: {base_vp_sum} + {tracked_bonus} = {tracked_total}",
            )
        )

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
        title_label = Label(
            text=title,
            font_size="22sp",
            size_hint=(1, 0.18),
            color=player_accent(player),
        )
        self.player_title_labels[player] = title_label
        panel.add_widget(title_label)

        for row_title, row_type, category in self.SCORE_ROWS:
            panel.add_widget(
                self._build_score_row(player, row_title, row_type, category)
            )

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
        row_label = Label(
            text=row_title,
            halign="left",
            size_hint=(0.5, 1),
            color=player_accent(player),
        )
        row.add_widget(row_label)

        minus_button = Button(text="-", size_hint=(0.15, 1))
        value_label = Label(text="0", size_hint=(0.2, 1), color=player_accent(player))
        plus_button = Button(text="+", size_hint=(0.15, 1))

        key = category if category is not None else "command_points"
        self.score_title_labels[(player, key)] = row_label
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

    def _build_total_row(self, player: str) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", spacing=8, size_hint=(1, 0.16))
        total_title_label = Label(
            text="Total VP",
            halign="left",
            size_hint=(0.6, 1),
            color=player_accent(player),
            bold=True,
        )
        row.add_widget(total_title_label)
        total_label = Label(
            text="0",
            size_hint=(0.4, 1),
            color=player_accent(player),
            bold=True,
        )
        self.total_title_labels[player] = total_title_label
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

    def _adjust_turning_point(self, direction: int) -> None:
        if self.game_state.end_game:
            return

        if direction > 0 and self.game_state.turning_point == TURN_MAX:
            self._request_end_game_transition()
            self.refresh_from_state()
            return

        next_turning_point = max(
            TURN_MIN,
            min(TURN_MAX, self.game_state.turning_point + direction),
        )
        self.game_state.turning_point = next_turning_point
        self.refresh_from_state()

    def _request_end_game_transition(self) -> None:
        if self.game_state.turning_point != TURN_MAX or self.game_state.end_game:
            self.refresh_from_state()
            return

        if self.end_game_handler is not None:
            self.end_game_handler()
        else:
            self.refresh_from_state()

    def _handle_secret_op_press(self, player: str, op: str, _instance: Button) -> None:
        self._set_secret_op(player, op)

    def _set_secret_op(self, player: str, op: str) -> None:
        self.game_state.set_secret_op(player, op)
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
        player_one_team = self.game_state.player_one_team or "Player One"
        player_two_team = self.game_state.player_two_team or "Player Two"
        self.matchup_label.text = f"{player_one_team} vs {player_two_team}"
        self.turning_point_label.text = (
            "End Game"
            if self.game_state.end_game
            else f"Turning Point {self.game_state.turning_point}"
        )
        self.turning_point_decrement_button.disabled = (
            self.game_state.end_game or self.game_state.turning_point == TURN_MIN
        )
        self.turning_point_increment_button.disabled = self.game_state.end_game
        self.turning_point_increment_button.background_color = (
            (1, 0.55, 0, 1)
            if self.game_state.turning_point == TURN_MAX
            else (1, 1, 1, 1)
        )

        self.end_game_controls.height = 120 if self.game_state.end_game else 0
        self.end_game_controls.opacity = 1 if self.game_state.end_game else 0

        both_revealed = (
            self.game_state.end_game
            and self.game_state.player_one.secret_op is not None
            and self.game_state.player_two.secret_op is not None
        )
        self.end_game_summary.height = 200 if both_revealed else 0
        self.end_game_summary.opacity = 1 if both_revealed else 0

        for button in self.secret_op_buttons.values():
            button.disabled = not self.game_state.end_game

        for player in ("player_one", "player_two"):
            selected_op = self.game_state._get_player_scores(player).secret_op
            selected_label = (
                self.SECRET_OP_LABELS[selected_op]
                if selected_op is not None
                else "None"
            )
            self.secret_op_status_labels[player].text = f"Selected: {selected_label}"

            for _label, op in self.SECRET_OPS:
                button = self.secret_op_buttons[(player, op)]
                is_selected = selected_op == op
                button.background_color = (
                    player_surface_selected(player)
                    if is_selected
                    else player_surface(player)
                )
                button.color = player_button_text(is_selected)

        if both_revealed:
            self.summary_player_labels["player_one"].text = self._format_player_summary(
                "player_one", "Player One Summary"
            )
            self.summary_player_labels["player_two"].text = self._format_player_summary(
                "player_two", "Player Two Summary"
            )
        else:
            self.summary_player_labels["player_one"].text = ""
            self.summary_player_labels["player_two"].text = ""

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
            self.total_value_labels[player].text = str(totals[player])
