"""High-level multi-screen flow for Kill Team Tracker."""

from __future__ import annotations

from collections.abc import Callable

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget

from app.state import STARTER_KILL_TEAMS, GameState
from app.ui.main_screen import MainGameScreen
from app.ui.player_palette import (
    player_accent,
    player_button_text,
    player_surface,
    player_surface_selected,
)


class HomeScreen(Screen):
    """Landing screen with primary Start Game action."""

    def __init__(self, on_start_game: Callable[[], None], **kwargs: object) -> None:
        super().__init__(name="home", **kwargs)
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(24),
        )
        layout.add_widget(
            Label(
                text="Kill Team Tracker",
                font_size="30sp",
                size_hint=(1, None),
                height=dp(80),
            )
        )
        layout.add_widget(Widget())

        self.start_game_button = Button(
            text="Start Game",
            size_hint=(1, None),
            height=dp(56),
            on_press=lambda _instance: on_start_game(),
        )
        self.stats_button = Button(
            text="Stats (Deferred)",
            size_hint=(1, None),
            height=dp(56),
            disabled=True,
        )
        self.stats_note_label = Label(
            text="Stats screen is planned for a later milestone.",
            size_hint=(1, None),
            height=dp(32),
        )

        layout.add_widget(self.start_game_button)
        layout.add_widget(self.stats_button)
        layout.add_widget(self.stats_note_label)
        self.add_widget(layout)


class TeamSelectionScreen(Screen):
    """Team selection screen with one team picker per player."""

    PLACEHOLDER_TEXT = "Select a Kill Team"

    def __init__(
        self,
        game_state: GameState,
        on_back: Callable[[], None],
        on_confirm: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(name="team_selection", **kwargs)
        self.game_state = game_state
        self.on_confirm = on_confirm
        self.team_spinners: dict[str, Spinner] = {}
        self.player_title_labels: dict[str, Label] = {}
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(24),
        )
        layout.add_widget(
            Label(
                text="Team Selection",
                font_size="28sp",
                size_hint=(1, None),
                height=dp(56),
            )
        )
        layout.add_widget(
            Label(
                text="Choose a team for each player before starting the match.",
                halign="center",
                size_hint=(1, None),
                height=dp(48),
            )
        )

        layout.add_widget(self._build_player_selector("player_one", "Player One"))
        layout.add_widget(self._build_player_selector("player_two", "Player Two"))

        self.selection_status_label = Label(
            text="Select both teams to continue.",
            size_hint=(1, None),
            height=dp(32),
        )
        layout.add_widget(self.selection_status_label)
        layout.add_widget(Widget())

        button_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(56),
        )
        back_button = Button(
            text="Back",
            size_hint=(1, None),
            height=dp(56),
            on_press=lambda _instance: on_back(),
        )
        self.confirm_button = Button(
            text="Confirm Teams",
            size_hint=(1, None),
            height=dp(56),
            disabled=True,
            on_press=lambda _instance: self._confirm_teams(),
        )
        button_row.add_widget(back_button)
        button_row.add_widget(self.confirm_button)
        layout.add_widget(button_row)
        self.add_widget(layout)
        self.refresh_from_state()

    def _build_player_selector(self, player: str, title: str) -> BoxLayout:
        container = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(112),
        )
        title_label = Label(
            text=title,
            font_size="20sp",
            size_hint=(1, None),
            height=dp(32),
            color=player_accent(player),
        )
        self.player_title_labels[player] = title_label
        container.add_widget(title_label)
        spinner = Spinner(
            text=self.PLACEHOLDER_TEXT,
            values=STARTER_KILL_TEAMS,
            size_hint=(1, None),
            height=dp(56),
            background_normal="",
            background_down="",
            background_color=player_surface(player),
            color=player_button_text(False),
        )
        spinner.bind(text=self._make_spinner_handler(player))
        self.team_spinners[player] = spinner
        container.add_widget(spinner)
        return container

    def _make_spinner_handler(self, player: str) -> Callable[[Spinner, str], None]:
        def handle_spinner_change(_instance: Spinner, value: str) -> None:
            self._handle_spinner_change(player, value)

        return handle_spinner_change

    def _handle_spinner_change(self, player: str, value: str) -> None:
        if value == self.PLACEHOLDER_TEXT:
            return
        self.game_state.set_team_selection(player, value)
        self.refresh_from_state()

    def _confirm_teams(self) -> None:
        try:
            self.game_state.validate_team_selection()
        except ValueError:
            self.refresh_from_state()
            return

        self.selection_status_label.text = "Teams confirmed"
        self.on_confirm()

    def refresh_from_state(self) -> None:
        player_one_team = self.game_state.player_one_team
        player_two_team = self.game_state.player_two_team

        self.team_spinners["player_one"].text = (
            player_one_team if player_one_team is not None else self.PLACEHOLDER_TEXT
        )
        self.team_spinners["player_two"].text = (
            player_two_team if player_two_team is not None else self.PLACEHOLDER_TEXT
        )

        teams_ready = self.game_state.has_team_selection()
        self.confirm_button.disabled = not teams_ready

        if teams_ready:
            self.selection_status_label.text = "Ready to start Turning Point 1"
        elif player_one_team is not None or player_two_team is not None:
            self.selection_status_label.text = "Select the remaining team to continue."
        else:
            self.selection_status_label.text = "Select both teams to continue."


class EndGameSelectionScreen(Screen):
    """End-game primary-op reveal screen with reversible navigation."""

    SECRET_OPS = (
        ("Tac Op", "tac_op"),
        ("Kill Op", "kill_op"),
        ("Crit Op", "crit_op"),
    )
    SECRET_OP_LABELS = {op: label for label, op in SECRET_OPS}

    def __init__(
        self,
        game_state: GameState,
        on_back: Callable[[], None],
        on_continue: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(name="end_game", **kwargs)
        self.game_state = game_state
        self.on_continue = on_continue
        self.secret_op_buttons: dict[tuple[str, str], Button] = {}
        self.secret_op_status_labels: dict[str, Label] = {}
        self.secret_op_title_labels: dict[str, Label] = {}
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(24),
        )
        layout.add_widget(
            Label(
                text="Reveal Primary Ops",
                font_size="28sp",
                size_hint=(1, None),
                height=dp(56),
            )
        )
        self.instructions_label = Label(
            text=(
                "Each player reveals their Primary Op. "
                "Continue unlocks once both are selected."
            ),
            halign="center",
            size_hint=(1, None),
            height=dp(56),
        )
        layout.add_widget(self.instructions_label)

        players_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint=(1, 1),
        )
        players_row.add_widget(self._build_secret_op_panel("player_one", "Player One"))
        players_row.add_widget(self._build_secret_op_panel("player_two", "Player Two"))
        layout.add_widget(players_row)

        self.status_label = Label(
            text="Select both Primary Ops to continue.",
            size_hint=(1, None),
            height=dp(32),
        )
        layout.add_widget(self.status_label)

        buttons_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(56),
        )
        self.back_button = Button(
            text="Back to Gameplay",
            size_hint=(0.5, None),
            height=dp(56),
            on_press=lambda _instance: on_back(),
        )
        self.continue_button = Button(
            text="Continue to Final Score",
            size_hint=(0.5, None),
            height=dp(56),
            disabled=True,
            on_press=lambda _instance: self._continue_to_final_score(),
        )
        buttons_row.add_widget(self.back_button)
        buttons_row.add_widget(self.continue_button)
        layout.add_widget(buttons_row)
        self.add_widget(layout)
        self.refresh_from_state()

    def _build_secret_op_panel(self, player: str, title: str) -> BoxLayout:
        panel = BoxLayout(orientation="vertical", spacing=dp(12), size_hint=(1, 1))
        title_label = Label(
            text=title,
            font_size="20sp",
            size_hint=(1, None),
            height=dp(32),
            color=player_accent(player),
        )
        self.secret_op_title_labels[player] = title_label
        panel.add_widget(title_label)

        button_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(56),
        )
        for label, op in self.SECRET_OPS:
            button = Button(
                text=label,
                size_hint=(1, None),
                height=dp(56),
                background_normal="",
                background_down="",
                background_color=player_surface(player),
                color=player_button_text(False),
            )
            button.bind(on_press=self._make_secret_op_handler(player, op))
            self.secret_op_buttons[(player, op)] = button
            button_row.add_widget(button)

        status_label = Label(
            text="Selected: None",
            size_hint=(1, None),
            height=dp(28),
            color=player_accent(player),
        )
        self.secret_op_status_labels[player] = status_label

        panel.add_widget(button_row)
        panel.add_widget(Widget())
        panel.add_widget(status_label)
        return panel

    def _make_secret_op_handler(self, player: str, op: str) -> Callable[[Button], None]:
        def handle_secret_op(_instance: Button) -> None:
            self._set_secret_op(player, op)

        return handle_secret_op

    def _set_secret_op(self, player: str, op: str) -> None:
        self.game_state.set_secret_op(player, op)
        self.refresh_from_state()

    def _continue_to_final_score(self) -> None:
        self.refresh_from_state()
        if self.continue_button.disabled:
            return
        self.on_continue()

    def refresh_from_state(self) -> None:
        both_revealed = True
        for player in ("player_one", "player_two"):
            selected_op = self.game_state._get_player_scores(player).secret_op
            if selected_op is None:
                both_revealed = False

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

        self.continue_button.disabled = not both_revealed
        if both_revealed:
            self.status_label.text = "Primary Ops locked in. Continue to final score."
        else:
            self.status_label.text = "Select both Primary Ops to continue."


class FinalScoreScreen(Screen):
    """Final-score view with save/discard actions and back recovery."""

    SECRET_OP_LABELS = {
        "tac_op": "Tac Op",
        "kill_op": "Kill Op",
        "crit_op": "Crit Op",
    }

    # Maps secret_op key -> (display label, scores attribute name)
    _OP_ROWS = [
        ("tac_op", "Tac Op", "tactical_vp"),
        ("kill_op", "Kill Op", "kill_vp"),
        ("crit_op", "Crit Op", "main_mission_vp"),
    ]

    def __init__(
        self,
        game_state: GameState,
        on_back: Callable[[], None],
        on_save: Callable[[], None],
        on_discard: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(name="final_score", **kwargs)
        self.game_state = game_state
        self.on_save = on_save
        self.on_discard = on_discard
        self._metric_labels: dict[str, Label] = {}
        self._header_labels: dict[str, Label] = {}

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(16),
        )

        root.add_widget(
            Label(
                text="Final Score",
                font_size="28sp",
                size_hint=(1, None),
                height=dp(44),
            )
        )

        self.winner_label = Label(
            text="",
            font_size="22sp",
            bold=True,
            size_hint=(1, None),
            height=dp(36),
        )
        self._bind_label_text_size(self.winner_label)
        root.add_widget(self.winner_label)

        self._content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            size_hint_y=None,
            height=dp(360),
        )
        root.add_widget(self._content)

        self._content.add_widget(self._build_table_header_row())

        self._op_labels: dict[tuple[str, str], Label] = {}
        for op_key, op_display, _attr in self._OP_ROWS:
            self._content.add_widget(self._build_table_row(op_key, op_display))

        self.p1_total_label = self._build_value_label(
            font_size="26sp",
            bold=True,
            color=player_accent("player_one"),
        )
        self.p2_total_label = self._build_value_label(
            font_size="26sp",
            bold=True,
            color=player_accent("player_two"),
        )
        self._content.add_widget(
            self._build_table_row(
                "total",
                "Total",
                player_one_label=self.p1_total_label,
                player_two_label=self.p2_total_label,
                row_height=dp(64),
                metric_font_size="18sp",
            )
        )

        buttons_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(56),
        )
        self.back_button = Button(
            text="Back",
            size_hint=(0.33, 1),
            on_press=lambda _instance: on_back(),
        )
        self.save_button = Button(
            text="Save Final Scores",
            size_hint=(0.33, 1),
            on_press=lambda _instance: self._handle_save(),
        )
        self.discard_button = Button(
            text="Discard Game",
            size_hint=(0.34, 1),
            on_press=lambda _instance: self._handle_discard(),
        )
        buttons_row.add_widget(self.back_button)
        buttons_row.add_widget(self.save_button)
        buttons_row.add_widget(self.discard_button)
        root.add_widget(buttons_row)
        self.add_widget(root)

    def _bind_label_text_size(self, label: Label) -> None:
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))

    def _build_value_label(
        self,
        *,
        font_size: str = "20sp",
        bold: bool = False,
        color: tuple[float, float, float, float] | None = None,
    ) -> Label:
        label_kwargs: dict[str, object] = {
            "text": "0",
            "font_size": font_size,
            "bold": bold,
            "halign": "center",
            "valign": "middle",
        }
        if color is not None:
            label_kwargs["color"] = color
        label = Label(**label_kwargs)
        self._bind_label_text_size(label)
        return label

    def _build_metric_label(self, text: str, *, font_size: str = "16sp") -> Label:
        label = Label(
            text=text,
            font_size=font_size,
            bold=True,
            halign="center",
            valign="middle",
        )
        self._bind_label_text_size(label)
        return label

    def _build_table_header_row(self) -> BoxLayout:
        row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            padding=[dp(6), dp(4), dp(6), dp(4)],
            size_hint=(1, None),
            height=dp(72),
        )
        team_lbl = Label(
            text="",
            font_size="17sp",
            bold=True,
            halign="center",
            valign="middle",
            size_hint=(0.36, 1),
            color=player_accent("player_one"),
        )
        self._bind_label_text_size(team_lbl)
        self._player_one_team_label = team_lbl
        self._header_labels["player_one"] = team_lbl

        metric_lbl = self._build_metric_label("Metric", font_size="17sp")
        metric_lbl.size_hint = (0.28, 1)
        self._metric_labels["header"] = metric_lbl

        opponent_lbl = Label(
            text="",
            font_size="17sp",
            bold=True,
            halign="center",
            valign="middle",
            size_hint=(0.36, 1),
            color=player_accent("player_two"),
        )
        self._bind_label_text_size(opponent_lbl)
        self._player_two_team_label = opponent_lbl
        self._header_labels["player_two"] = opponent_lbl

        row.add_widget(team_lbl)
        row.add_widget(metric_lbl)
        row.add_widget(opponent_lbl)
        return row

    def _build_table_row(
        self,
        metric_key: str,
        metric_text: str,
        *,
        player_one_label: Label | None = None,
        player_two_label: Label | None = None,
        row_height: float | None = None,
        metric_font_size: str = "16sp",
    ) -> BoxLayout:
        row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            padding=[dp(6), dp(6), dp(6), dp(6)],
            size_hint=(1, None),
            height=row_height or dp(54),
        )

        p1_label = player_one_label or self._build_value_label(
            color=player_accent("player_one")
        )
        p1_label.size_hint = (0.36, 1)
        if metric_key != "total":
            self._op_labels[("player_one", metric_key)] = p1_label

        metric_label = self._build_metric_label(metric_text, font_size=metric_font_size)
        metric_label.size_hint = (0.28, 1)
        self._metric_labels[metric_key] = metric_label

        p2_label = player_two_label or self._build_value_label(
            color=player_accent("player_two")
        )
        p2_label.size_hint = (0.36, 1)
        if metric_key != "total":
            self._op_labels[("player_two", metric_key)] = p2_label

        row.add_widget(p1_label)
        row.add_widget(metric_label)
        row.add_widget(p2_label)
        return row

    def _handle_save(self) -> None:
        self.on_save()

    def _handle_discard(self) -> None:
        self.on_discard()

    def refresh_from_state(self) -> None:
        for player, total_label in (
            ("player_one", self.p1_total_label),
            ("player_two", self.p2_total_label),
        ):
            scores = self.game_state._get_player_scores(player)
            team_name = getattr(self.game_state, f"{player}_team") or (
                "Player One" if player == "player_one" else "Player Two"
            )
            selected_op = scores.secret_op
            bonus_vp = self.game_state.calculate_bonus_vp(player)
            total = self.game_state.total_vp(player)

            team_lbl: Label = getattr(self, f"_{player}_team_label")
            team_lbl.text = team_name

            for op_key, op_display, attr in self._OP_ROWS:
                vp_val = getattr(scores, attr)
                lbl = self._op_labels[(player, op_key)]
                if op_key == selected_op:
                    lbl.text = f"{vp_val} +{bonus_vp}"
                else:
                    lbl.text = str(vp_val)

            total_label.text = str(total)

        p1_total = self.game_state.total_vp("player_one")
        p2_total = self.game_state.total_vp("player_two")
        if p1_total > p2_total:
            p1_team = self.game_state.player_one_team or "Player One"
            self.winner_label.text = f"{p1_team} WIN!"
            self.winner_label.color = player_accent("player_one")
        elif p2_total > p1_total:
            p2_team = self.game_state.player_two_team or "Player Two"
            self.winner_label.text = f"{p2_team} WIN!"
            self.winner_label.color = player_accent("player_two")
        else:
            self.winner_label.text = "DRAW"
            self.winner_label.color = (0.18, 0.18, 0.18, 1)


class TrackerFlow(ScreenManager):
    """Screen manager hosting the app screens and navigation flow."""

    def __init__(
        self,
        game_state: GameState,
        save_handler: Callable[[dict[str, object]], None] | None = None,
        resume_handler: Callable[[], dict[str, object]] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(transition=NoTransition(), **kwargs)
        self.game_state = game_state
        self.home_screen = HomeScreen(on_start_game=self.go_to_team_selection)
        self.team_selection_screen = TeamSelectionScreen(
            game_state=game_state,
            on_back=self.go_to_home,
            on_confirm=self.start_gameplay,
        )
        self.gameplay_screen = Screen(name="gameplay")
        self.end_game_screen = EndGameSelectionScreen(
            game_state=game_state,
            on_back=self.return_to_gameplay,
            on_continue=self.go_to_final_score,
        )
        self.final_score_screen = FinalScoreScreen(
            game_state=game_state,
            on_back=self.go_to_end_game,
            on_save=self._handle_save_final_scores,
            on_discard=self._handle_discard_game,
        )
        self.main_game_screen = MainGameScreen(
            game_state=game_state,
            end_game_handler=self.go_to_end_game,
            save_handler=save_handler,
            resume_handler=resume_handler,
        )
        self.gameplay_screen.add_widget(self.main_game_screen)

        self.add_widget(self.home_screen)
        self.add_widget(self.team_selection_screen)
        self.add_widget(self.gameplay_screen)
        self.add_widget(self.end_game_screen)
        self.add_widget(self.final_score_screen)
        self.current = "home"

    def go_to_home(self) -> None:
        self.current = "home"

    def go_to_team_selection(self) -> None:
        self.game_state.reset_game()
        self.team_selection_screen.refresh_from_state()
        self.main_game_screen.refresh_from_state()
        self.current = "team_selection"

    def start_gameplay(self) -> None:
        self.game_state.turning_point = 1
        self.game_state.end_game = False
        self.main_game_screen.refresh_from_state()
        self.current = "gameplay"

    def return_to_gameplay(self) -> None:
        self.game_state.end_game = False
        self.main_game_screen.refresh_from_state()
        self.current = "gameplay"

    def go_to_end_game(self) -> None:
        self.game_state.end_game = True
        self.end_game_screen.refresh_from_state()
        self.current = "end_game"

    def go_to_final_score(self) -> None:
        self.game_state.end_game = True
        self.final_score_screen.refresh_from_state()
        self.current = "final_score"

    def _handle_save_final_scores(self) -> None:
        """Save final scores (placeholder for future stats pool integration)."""
        # TODO: Wire to stats/history storage adapter in future milestone
        self.go_to_home()

    def _handle_discard_game(self) -> None:
        """Discard game and return to home."""
        self.game_state.reset_game()
        self.go_to_home()
