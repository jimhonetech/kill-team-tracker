"""Core state models for Kill Team Tracker V1."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

TURN_MIN = 1
TURN_MAX = 4
CP_MIN = 0
CP_MAX = 6
VP_MIN = 0
VP_MAX = 15
SCHEMA_VERSION = 2
VP_CATEGORIES = ("tactical_vp", "kill_vp", "main_mission_vp")
SECRET_OP_CHOICES = ("tac_op", "kill_op", "crit_op")


def _validate_range(name: str, value: int, minimum: int, maximum: int) -> None:
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}, got {value}")


def _validate_positive_amount(amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")


def _apply_bounded_delta(current: int, delta: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, current + delta))


def _validate_secret_op(secret_op: str | None) -> None:
    if secret_op is not None and secret_op not in SECRET_OP_CHOICES:
        raise ValueError(
            f"secret_op must be one of {SECRET_OP_CHOICES} or None, got {secret_op!r}"
        )


def _validate_end_game(end_game: bool) -> None:
    if not isinstance(end_game, bool):
        raise ValueError("end_game must be a boolean")


def _coerce_int_field(
    data: dict[str, object], field_name: str, default: int = 0
) -> int:
    raw_value = data.get(field_name, default)
    try:
        coerced_value: int = int(raw_value)
        return coerced_value
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def _coerce_secret_op_field(data: dict[str, object]) -> str | None:
    raw_value = data.get("secret_op")
    if raw_value is None:
        return None
    if not isinstance(raw_value, str):
        raise ValueError("secret_op must be a string or null")
    return raw_value


@dataclass(slots=True)
class PlayerScores:
    """V2 score fields for one player."""

    command_points: int = 0
    tactical_vp: int = 0
    kill_vp: int = 0
    main_mission_vp: int = 0
    bonus_vp: int = 0
    secret_op: str | None = None

    def __post_init__(self) -> None:
        _validate_range("command_points", self.command_points, CP_MIN, CP_MAX)
        _validate_range("tactical_vp", self.tactical_vp, VP_MIN, VP_MAX)
        _validate_range("kill_vp", self.kill_vp, VP_MIN, VP_MAX)
        _validate_range("main_mission_vp", self.main_mission_vp, VP_MIN, VP_MAX)
        _validate_range("bonus_vp", self.bonus_vp, VP_MIN, VP_MAX)
        _validate_secret_op(self.secret_op)

    def to_dict(self) -> dict[str, int | str | None]:
        return {
            "command_points": self.command_points,
            "tactical_vp": self.tactical_vp,
            "kill_vp": self.kill_vp,
            "main_mission_vp": self.main_mission_vp,
            "bonus_vp": self.bonus_vp,
            "secret_op": self.secret_op,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PlayerScores:
        return cls(
            command_points=_coerce_int_field(data, "command_points"),
            tactical_vp=_coerce_int_field(data, "tactical_vp"),
            kill_vp=_coerce_int_field(data, "kill_vp"),
            main_mission_vp=_coerce_int_field(data, "main_mission_vp"),
            bonus_vp=_coerce_int_field(data, "bonus_vp"),
            secret_op=_coerce_secret_op_field(data),
        )


@dataclass(slots=True)
class GameState:
    """Top-level V2 game state with stable serialization keys."""

    turning_point: int = 1
    player_one: PlayerScores = field(default_factory=PlayerScores)
    player_two: PlayerScores = field(default_factory=PlayerScores)
    selected_operation: str | None = None
    end_game: bool = False

    def __post_init__(self) -> None:
        _validate_range("turning_point", self.turning_point, TURN_MIN, TURN_MAX)
        _validate_end_game(self.end_game)

    def _get_player_scores(self, player: str) -> PlayerScores:
        if player == "player_one":
            return self.player_one
        if player == "player_two":
            return self.player_two
        raise ValueError(f"unknown player: {player}")

    def increment_command_points(self, player: str, amount: int = 1) -> int:
        _validate_positive_amount(amount)
        scores = self._get_player_scores(player)
        scores.command_points = _apply_bounded_delta(
            scores.command_points, amount, CP_MIN, CP_MAX
        )
        return scores.command_points

    def decrement_command_points(self, player: str, amount: int = 1) -> int:
        _validate_positive_amount(amount)
        scores = self._get_player_scores(player)
        scores.command_points = _apply_bounded_delta(
            scores.command_points, -amount, CP_MIN, CP_MAX
        )
        return scores.command_points

    def increment_vp(self, player: str, category: str, amount: int = 1) -> int:
        _validate_positive_amount(amount)
        if category not in VP_CATEGORIES:
            raise ValueError(f"unknown VP category: {category}")

        scores = self._get_player_scores(player)
        current = getattr(scores, category)
        updated = _apply_bounded_delta(current, amount, VP_MIN, VP_MAX)
        setattr(scores, category, updated)
        return updated

    def decrement_vp(self, player: str, category: str, amount: int = 1) -> int:
        _validate_positive_amount(amount)
        if category not in VP_CATEGORIES:
            raise ValueError(f"unknown VP category: {category}")

        scores = self._get_player_scores(player)
        current = getattr(scores, category)
        updated = _apply_bounded_delta(current, -amount, VP_MIN, VP_MAX)
        setattr(scores, category, updated)
        return updated

    def select_operation(self, operation: str | None) -> str | None:
        if operation is None:
            self.selected_operation = None
            return self.selected_operation

        normalized = operation.strip()
        if not normalized:
            raise ValueError("operation must be a non-empty string")

        self.selected_operation = normalized
        return self.selected_operation

    def set_secret_op(self, player: str, op: str) -> str:
        _validate_secret_op(op)
        scores = self._get_player_scores(player)
        scores.secret_op = op
        return scores.secret_op

    def set_bonus_vp(self, player: str, points: int) -> int:
        scores = self._get_player_scores(player)
        scores.bonus_vp = _apply_bounded_delta(0, points, VP_MIN, VP_MAX)
        return scores.bonus_vp

    def calculate_bonus_vp(self, player: str) -> int:
        """Calculate bonus VP as 50% of selected op, rounded up.

        Args:
            player: "player_one" or "player_two"

        Returns:
            50% of op VP (ceil), or 0 if no op selected.

        Raises:
            ValueError: if player is invalid or secret_op is invalid.
        """
        scores = self._get_player_scores(player)

        if scores.secret_op is None:
            return 0

        if scores.secret_op == "tac_op":
            op_vp = scores.tactical_vp
        elif scores.secret_op == "kill_op":
            op_vp = scores.kill_vp
        elif scores.secret_op == "crit_op":
            op_vp = scores.main_mission_vp
        else:
            raise ValueError(
                f"invalid secret_op: {scores.secret_op!r}; "
                f"must be one of {SECRET_OP_CHOICES}"
            )

        return math.ceil(op_vp / 2)

    def total_vp(self, player: str) -> int:
        scores = self._get_player_scores(player)
        return (
            scores.tactical_vp
            + scores.kill_vp
            + scores.main_mission_vp
            + scores.bonus_vp
        )

    def final_scores(self) -> dict[str, int]:
        return {
            "player_one": self.total_vp("player_one"),
            "player_two": self.total_vp("player_two"),
        }

    def reset_game(self) -> None:
        self.turning_point = TURN_MIN
        self.end_game = False
        self.selected_operation = None
        self.player_one = PlayerScores()
        self.player_two = PlayerScores()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "turning_point": self.turning_point,
            "end_game": self.end_game,
            "selected_operation": self.selected_operation,
            "players": {
                "player_one": self.player_one.to_dict(),
                "player_two": self.player_two.to_dict(),
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> GameState:
        raw_schema_version = data.get("schema_version")
        if raw_schema_version is None:
            raise ValueError("schema_version is required")

        if "turning_point" not in data:
            raise ValueError("turning_point is required")

        if "players" not in data:
            raise ValueError("players is required")

        try:
            schema_version = int(raw_schema_version)
        except (TypeError, ValueError) as exc:
            raise ValueError("schema_version must be an integer") from exc

        if schema_version != SCHEMA_VERSION:
            raise ValueError(
                f"unsupported schema_version: {schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )

        turning_point = int(data["turning_point"])
        end_game_raw = data.get("end_game", False)
        selected_operation_raw = data.get("selected_operation")

        if not isinstance(end_game_raw, bool):
            raise ValueError("end_game must be a boolean")

        if selected_operation_raw is None:
            selected_operation = None
        elif isinstance(selected_operation_raw, str):
            selected_operation = selected_operation_raw.strip() or None
        else:
            raise ValueError("selected_operation must be a string or null")

        players_raw = data["players"]
        if not isinstance(players_raw, dict):
            raise ValueError("players must be a dictionary")

        player_one_raw = players_raw.get("player_one", {})
        player_two_raw = players_raw.get("player_two", {})

        if not isinstance(player_one_raw, dict) or not isinstance(player_two_raw, dict):
            raise ValueError("player score payloads must be dictionaries")

        return cls(
            turning_point=turning_point,
            player_one=PlayerScores.from_dict(player_one_raw),
            player_two=PlayerScores.from_dict(player_two_raw),
            selected_operation=selected_operation,
            end_game=end_game_raw,
        )

    @classmethod
    def from_json(cls, payload: str) -> GameState:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("JSON payload is invalid") from exc

        if not isinstance(data, dict):
            raise ValueError("JSON payload must decode to an object")
        return cls.from_dict(data)
