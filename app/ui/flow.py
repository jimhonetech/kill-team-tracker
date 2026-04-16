"""High-level multi-screen flow for Kill Team Tracker."""

from __future__ import annotations

from collections.abc import Callable

try:
    from kivy.graphics import Color, Rectangle
except ImportError:  # pragma: no cover - fake-kivy test doubles omit graphics
    Color = None
    Rectangle = None

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
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

    def __init__(
        self,
        on_start_game: Callable[[], None],
        on_open_stats: Callable[[], None],
        **kwargs: object,
    ) -> None:
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
            text="Stats",
            size_hint=(1, None),
            height=dp(56),
            on_press=lambda _instance: on_open_stats(),
        )

        layout.add_widget(self.start_game_button)
        layout.add_widget(self.stats_button)
        self.add_widget(layout)


class StatsScreen(Screen):
    """Read-only stats shell with segmented navigation for multiple views."""

    VIEW_WIN_RATES = "win_rates"
    VIEW_OP_ANALYTICS = "op_analytics"
    _SCREEN_BACKGROUND_COLOR = (0.09, 0.11, 0.13, 1)
    _TEXT_PRIMARY = (0.97, 0.98, 0.99, 1)
    _TEXT_MUTED = (0.79, 0.84, 0.88, 1)
    _TEXT_ERROR = (1, 0.72, 0.66, 1)
    _OP_ORDER = ("tac_op", "kill_op", "crit_op")
    _SCOPE_ORDER = ("player_one", "player_two", "combined")
    _SCOPE_LABELS = {
        "player_one": "Player One",
        "player_two": "Player Two",
        "combined": "Combined",
    }

    def __init__(
        self,
        on_back: Callable[[], None],
        read_stats_summary_handler: Callable[[], dict[str, object]] | None = None,
        read_win_rate_summary_handler: Callable[[], dict[str, object]] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(name="stats", **kwargs)
        self.read_stats_summary_handler = (
            read_stats_summary_handler or read_win_rate_summary_handler
        )
        self.view_buttons: dict[str, Button] = {}

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(16),
        )
        self._apply_background(root, self._SCREEN_BACKGROUND_COLOR)
        root.add_widget(
            Label(
                text="Stats",
                font_size="28sp",
                color=self._TEXT_PRIMARY,
                size_hint=(1, None),
                height=dp(44),
            )
        )

        self.summary_label = self._build_text_label(
            font_size="17sp",
            bold=True,
            color=self._TEXT_PRIMARY,
        )
        root.add_widget(self.summary_label)

        self.error_label = self._build_text_label(
            font_size="15sp",
            color=self._TEXT_ERROR,
        )
        root.add_widget(self.error_label)

        view_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(48),
        )
        self.win_rates_button = self._build_view_button(
            "Win Rates",
            self.VIEW_WIN_RATES,
        )
        self.op_analytics_button = self._build_view_button(
            "Op Analytics",
            self.VIEW_OP_ANALYTICS,
        )
        view_row.add_widget(self.win_rates_button)
        view_row.add_widget(self.op_analytics_button)
        root.add_widget(view_row)

        self.stats_views = ScreenManager(transition=NoTransition())

        self.win_rates_screen = Screen(name=self.VIEW_WIN_RATES)
        self.win_rates_screen.add_widget(self._build_win_rates_layout())
        self.stats_views.add_widget(self.win_rates_screen)

        self.op_analytics_screen = Screen(name=self.VIEW_OP_ANALYTICS)
        self.op_analytics_screen.add_widget(self._build_op_analytics_layout())
        self.stats_views.add_widget(self.op_analytics_screen)

        root.add_widget(self.stats_views)

        back_row = BoxLayout(size_hint=(1, None), height=dp(56))
        self.back_button = Button(
            text="Back to Home",
            on_press=lambda _instance: on_back(),
        )
        back_row.add_widget(self.back_button)
        root.add_widget(back_row)

        self.add_widget(root)
        self.show_view(self.VIEW_WIN_RATES)

    def _build_view_button(self, text: str, view_name: str) -> Button:
        button = Button(
            text=text,
            size_hint=(0.5, 1),
            background_normal="",
            background_down="",
            on_press=lambda _instance: self.show_view(view_name),
        )
        self.view_buttons[view_name] = button
        return button

    def _build_win_rates_layout(self) -> ScrollView:
        scroll = ScrollView(size_hint=(1, 1))
        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(1, None),
            padding=[0, 0, 0, dp(8)],
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)

        self.empty_history_label = self._build_text_label(
            font_size="16sp",
            color=self._TEXT_MUTED,
        )
        self.content.add_widget(self.empty_history_label)

        self.slot_stats_label = self._build_section_label("Player Slot Win Rates")
        self.content.add_widget(self.slot_stats_label)
        self.team_overall_label = self._build_section_label("Team Win Rates - Overall")
        self.content.add_widget(self.team_overall_label)
        self.team_player_one_label = self._build_section_label(
            "Team Win Rates - As Player One"
        )
        self.content.add_widget(self.team_player_one_label)
        self.team_player_two_label = self._build_section_label(
            "Team Win Rates - As Player Two"
        )
        self.content.add_widget(self.team_player_two_label)
        return scroll

    def _build_op_analytics_layout(self) -> ScrollView:
        scroll = ScrollView(size_hint=(1, 1))
        self.op_analytics_content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(1, None),
            padding=[0, dp(8), 0, dp(8)],
        )
        self.op_analytics_content.bind(
            minimum_height=self.op_analytics_content.setter("height")
        )
        scroll.add_widget(self.op_analytics_content)

        self.op_analytics_empty_label = self._build_text_label(
            font_size="16sp",
            color=self._TEXT_MUTED,
        )
        self.op_analytics_content.add_widget(self.op_analytics_empty_label)

        self.op_analytics_scope_labels: dict[str, Label] = {}
        for scope in self._SCOPE_ORDER:
            section_label = self._build_section_label(
                f"Primary Op Analytics - {self._SCOPE_LABELS[scope]}"
            )
            self.op_analytics_content.add_widget(section_label)
            self.op_analytics_scope_labels[scope] = section_label

        return scroll

    def _format_op_summary(self, op_stats: object) -> str:
        if not isinstance(op_stats, dict):
            return "No data."

        picks = self._coerce_int(op_stats.get("picks"))
        wins = self._coerce_int(op_stats.get("wins"))
        draws = self._coerce_int(op_stats.get("draws"))
        losses = self._coerce_int(op_stats.get("losses"))
        win_pct = self._coerce_float(op_stats.get("win_percentage"))
        avg_selected_vp = self._coerce_float(op_stats.get("average_selected_vp"))
        avg_bonus_vp = self._coerce_float(op_stats.get("average_bonus_vp"))
        return (
            f"{picks} picks, {win_pct:.2f}% win "
            f"({wins}W {draws}D {losses}L), "
            f"avg selected VP {avg_selected_vp:.2f}, avg bonus VP {avg_bonus_vp:.2f}"
        )

    def _render_scope_analytics(
        self,
        scope: str,
        primary_ops: object,
        op_buckets: object,
    ) -> str:
        heading = f"Primary Op Analytics - {self._SCOPE_LABELS[scope]}"

        if not isinstance(primary_ops, dict):
            return "\n".join((heading, "No Primary Op analytics data."))

        scope_primary = primary_ops.get(scope)
        if not isinstance(scope_primary, dict):
            return "\n".join((heading, "No Primary Op analytics data."))

        most_successful = scope_primary.get("most_successful")
        if isinstance(most_successful, dict):
            best_label_obj = most_successful.get("label")
            if isinstance(best_label_obj, str) and best_label_obj.strip():
                best_label = best_label_obj.strip()
            else:
                best_label = "None"
            tied_ops_obj = most_successful.get("tied_ops")
            if isinstance(tied_ops_obj, list):
                tied_count = len(tied_ops_obj)
            else:
                tied_count = 0
        else:
            best_label = "None"
            tied_count = 0

        player_entries = self._coerce_int(scope_primary.get("player_entries"))
        revealed = self._coerce_int(scope_primary.get("revealed_primary_ops"))
        missing = self._coerce_int(scope_primary.get("missing_primary_ops"))

        lines = [
            heading,
            f"Most successful Primary Op: {best_label}",
            (
                "Primary Op picks considered: "
                f"{revealed}/{player_entries} revealed ({missing} missing)"
            ),
        ]
        if tied_count > 1:
            lines.append(f"Most successful tie: {tied_count} ops")

        lines.append("Primary Op pick counts + win rates")
        ops_stats = scope_primary.get("ops")
        if isinstance(ops_stats, dict):
            for op_key in self._OP_ORDER:
                op_entry = ops_stats.get(op_key)
                if isinstance(op_entry, dict):
                    label_obj = op_entry.get("label")
                    label = (
                        label_obj.strip()
                        if isinstance(label_obj, str) and label_obj.strip()
                        else op_key
                    )
                else:
                    label = op_key
                lines.append(f"- {label}: {self._format_op_summary(op_entry)}")
        else:
            lines.append("- No Primary Op pick data.")

        lines.append("Supporting Tac Op / Kill Op / Crit Op performance")
        if isinstance(op_buckets, dict):
            for op_key in self._OP_ORDER:
                bucket = op_buckets.get(op_key)
                label = op_key
                scope_bucket = None
                if isinstance(bucket, dict):
                    label_obj = bucket.get("label")
                    if isinstance(label_obj, str) and label_obj.strip():
                        label = label_obj.strip()
                    scoped = bucket.get(scope)
                    if isinstance(scoped, dict):
                        scope_bucket = scoped

                if scope_bucket is None:
                    lines.append(f"- {label}: No data.")
                    continue

                matches = self._coerce_int(scope_bucket.get("matches"))
                wins = self._coerce_int(scope_bucket.get("wins"))
                draws = self._coerce_int(scope_bucket.get("draws"))
                losses = self._coerce_int(scope_bucket.get("losses"))
                win_pct = self._coerce_float(scope_bucket.get("win_percentage"))
                avg_vp = self._coerce_float(scope_bucket.get("average_vp"))
                selected_as_primary = self._coerce_int(
                    scope_bucket.get("selected_as_primary")
                )
                avg_bonus_when_primary = self._coerce_float(
                    scope_bucket.get("average_bonus_vp_when_primary")
                )
                lines.append(
                    (
                        f"- {label}: {matches} matches, {win_pct:.2f}% win "
                        f"({wins}W {draws}D {losses}L), avg VP {avg_vp:.2f}, "
                        "selected as Primary "
                        f"{selected_as_primary}x, avg bonus when Primary "
                        f"{avg_bonus_when_primary:.2f}"
                    )
                )
        else:
            lines.append("- No supporting op performance data.")

        return "\n".join(lines)

    def show_view(self, view_name: str) -> None:
        if view_name not in self.view_buttons:
            return
        self.stats_views.current = view_name
        self._sync_view_button_state(view_name)

    def _sync_view_button_state(self, active_view: str) -> None:
        selected_color = (0.14, 0.36, 0.28, 1)
        idle_color = (0.24, 0.28, 0.31, 1)
        for view_name, button in self.view_buttons.items():
            is_active = view_name == active_view
            button.background_color = selected_color if is_active else idle_color
            button.color = self._TEXT_PRIMARY

    def _apply_background(
        self,
        widget: Widget,
        color: tuple[float, float, float, float],
    ) -> None:
        if Color is None or Rectangle is None or not hasattr(widget, "canvas"):
            return

        with widget.canvas.before:
            Color(*color)
            background = Rectangle(pos=widget.pos, size=widget.size)

        def _sync_background(_instance: Widget, _value: object) -> None:
            background.pos = widget.pos
            background.size = widget.size

        widget.bind(pos=_sync_background, size=_sync_background)

    def _build_text_label(
        self,
        *,
        font_size: str = "16sp",
        bold: bool = False,
        color: tuple[float, float, float, float] | None = None,
    ) -> Label:
        kwargs: dict[str, object] = {
            "text": "",
            "font_size": font_size,
            "bold": bold,
            "halign": "left",
            "valign": "top",
            "size_hint": (1, None),
        }
        if color is not None:
            kwargs["color"] = color
        label = Label(**kwargs)
        label.bind(width=self._bind_label_text_size)
        label.bind(texture_size=self._bind_label_height)
        return label

    def _build_section_label(self, title: str) -> Label:
        label = self._build_text_label(font_size="15sp", color=self._TEXT_PRIMARY)
        label.text = title
        return label

    def _bind_label_text_size(self, label: Label, value: float) -> None:
        label.text_size = (value, None)

    def _bind_label_height(
        self, label: Label, texture_size: tuple[float, float]
    ) -> None:
        label.height = max(dp(24), texture_size[1])

    def _coerce_int(self, value: object) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return 0
        return 0

    def _coerce_float(self, value: object) -> float:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                return 0.0
        return 0.0

    def _render_team_section(self, title: str, teams: object, slot_key: str) -> str:
        if not isinstance(teams, dict) or not teams:
            return f"{title}\nNo team data yet."

        rows: list[str] = [title]
        team_rows: list[tuple[float, int, str, int, int, int]] = []
        for team_name in teams.keys():
            team_stats = teams.get(team_name)
            if not isinstance(team_stats, dict):
                continue
            slot_stats = team_stats.get(slot_key)
            if not isinstance(slot_stats, dict):
                continue
            wins = self._coerce_int(slot_stats.get("wins"))
            draws = self._coerce_int(slot_stats.get("draws"))
            losses = self._coerce_int(slot_stats.get("losses"))
            matches = self._coerce_int(slot_stats.get("matches"))
            percentage = self._coerce_float(slot_stats.get("win_percentage"))
            team_rows.append((percentage, matches, str(team_name), wins, draws, losses))

        for percentage, matches, team_name, wins, draws, losses in sorted(
            team_rows,
            key=lambda row: (-row[0], -row[1], row[2].lower()),
        ):
            rows.append(
                (
                    f"{team_name}: {percentage:.2f}% "
                    f"({wins}W {draws}D {losses}L / {matches}M)"
                )
            )

        if len(rows) == 1:
            rows.append("No team data yet.")
        return "\n".join(rows)

    def _clear_win_rate_content(self) -> None:
        self.slot_stats_label.text = ""
        self.team_overall_label.text = ""
        self.team_player_one_label.text = ""
        self.team_player_two_label.text = ""
        self.empty_history_label.text = ""

    def _clear_op_analytics_content(self) -> None:
        self.op_analytics_empty_label.text = ""
        for scope in self._SCOPE_ORDER:
            self.op_analytics_scope_labels[scope].text = ""

    def refresh_from_source(self) -> None:
        self.error_label.text = ""
        self._clear_win_rate_content()
        self._clear_op_analytics_content()

        if self.read_stats_summary_handler is None:
            self.summary_label.text = "Stats unavailable"
            self.error_label.text = (
                "Could not load stats: stats reader is not configured."
            )
            return

        try:
            summary = self.read_stats_summary_handler()
        except Exception as exc:
            self.summary_label.text = "Stats unavailable"
            self.error_label.text = f"Could not load stats: {exc}"
            return

        if not isinstance(summary, dict):
            self.summary_label.text = "Stats unavailable"
            self.error_label.text = "Could not load stats: unexpected summary format."
            return

        total_matches = self._coerce_int(summary.get("total_matches"))
        draws = self._coerce_int(summary.get("draws"))
        player_slots = summary.get("player_slots")
        teams = summary.get("teams")
        primary_ops = summary.get("primary_ops")
        op_buckets = summary.get("op_buckets")

        self.summary_label.text = f"Matches: {total_matches}   Draws: {draws}"
        if total_matches == 0:
            self.empty_history_label.text = (
                "No match history yet. Play and save a game to see stats."
            )
            self.op_analytics_empty_label.text = (
                "No match history yet. Play and save a game to see "
                "Primary Op analytics."
            )
        else:
            self.empty_history_label.text = ""
            self.op_analytics_empty_label.text = ""

        if isinstance(player_slots, dict):
            p1 = player_slots.get("player_one")
            p2 = player_slots.get("player_two")
        else:
            p1 = None
            p2 = None

        p1_wins = self._coerce_int(p1.get("wins")) if isinstance(p1, dict) else 0
        p1_draws = self._coerce_int(p1.get("draws")) if isinstance(p1, dict) else 0
        p1_losses = self._coerce_int(p1.get("losses")) if isinstance(p1, dict) else 0
        p1_matches = self._coerce_int(p1.get("matches")) if isinstance(p1, dict) else 0
        p1_pct = (
            self._coerce_float(p1.get("win_percentage"))
            if isinstance(p1, dict)
            else 0.0
        )

        p2_wins = self._coerce_int(p2.get("wins")) if isinstance(p2, dict) else 0
        p2_draws = self._coerce_int(p2.get("draws")) if isinstance(p2, dict) else 0
        p2_losses = self._coerce_int(p2.get("losses")) if isinstance(p2, dict) else 0
        p2_matches = self._coerce_int(p2.get("matches")) if isinstance(p2, dict) else 0
        p2_pct = (
            self._coerce_float(p2.get("win_percentage"))
            if isinstance(p2, dict)
            else 0.0
        )

        self.slot_stats_label.text = "\n".join(
            (
                "Player Slot Win Rates",
                (
                    f"Player One: {p1_pct:.2f}% "
                    f"({p1_wins}W {p1_draws}D {p1_losses}L / {p1_matches}M)"
                ),
                (
                    f"Player Two: {p2_pct:.2f}% "
                    f"({p2_wins}W {p2_draws}D {p2_losses}L / {p2_matches}M)"
                ),
            )
        )

        self.team_overall_label.text = self._render_team_section(
            "Team Win Rates - Overall",
            teams,
            "overall",
        )
        self.team_player_one_label.text = self._render_team_section(
            "Team Win Rates - As Player One",
            teams,
            "player_one",
        )
        self.team_player_two_label.text = self._render_team_section(
            "Team Win Rates - As Player Two",
            teams,
            "player_two",
        )

        for scope in self._SCOPE_ORDER:
            self.op_analytics_scope_labels[scope].text = self._render_scope_analytics(
                scope,
                primary_ops,
                op_buckets,
            )


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
        history_append_handler: Callable[[dict[str, object]], object] | None = None,
        read_stats_summary_handler: Callable[[], dict[str, object]] | None = None,
        read_win_rate_summary_handler: Callable[[], dict[str, object]] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(transition=NoTransition(), **kwargs)
        self.game_state = game_state
        self.home_screen = HomeScreen(
            on_start_game=self.go_to_team_selection,
            on_open_stats=self.go_to_stats,
        )
        self.stats_screen = StatsScreen(
            on_back=self.go_to_home,
            read_stats_summary_handler=(
                read_stats_summary_handler or read_win_rate_summary_handler
            ),
        )
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
        self.history_append_handler = history_append_handler
        self.gameplay_screen.add_widget(self.main_game_screen)

        self.add_widget(self.home_screen)
        self.add_widget(self.stats_screen)
        self.add_widget(self.team_selection_screen)
        self.add_widget(self.gameplay_screen)
        self.add_widget(self.end_game_screen)
        self.add_widget(self.final_score_screen)
        self.current = "home"

    def go_to_home(self) -> None:
        self.current = "home"

    def go_to_stats(self) -> None:
        self.stats_screen.show_view(StatsScreen.VIEW_WIN_RATES)
        self.stats_screen.refresh_from_source()
        self.current = "stats"

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
        """Archive final scores and return home."""
        if self.history_append_handler is not None:
            try:
                self.history_append_handler(self.game_state.to_dict())
            except Exception as exc:
                import traceback

                traceback.print_exc()
                print(f"[KillTeamTracker] ERROR: failed to save match history: {exc}")
        self.go_to_home()

    def _handle_discard_game(self) -> None:
        """Discard game and return to home."""
        self.game_state.reset_game()
        self.go_to_home()
