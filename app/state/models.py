"""Core state models for Kill Team Tracker V1."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

TURN_MIN = 1
TURN_MAX = 4
CP_MIN = 0
CP_MAX = 6
VP_MIN = 0
VP_MAX = 15
SCHEMA_VERSION = 1
VP_CATEGORIES = ("tactical_vp", "kill_vp", "main_mission_vp")


def _validate_range(name: str, value: int, minimum: int, maximum: int) -> None:
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}, got {value}")


def _validate_positive_amount(amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")


def _apply_bounded_delta(current: int, delta: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, current + delta))


@dataclass(slots=True)
class PlayerScores:
    """V1 score fields for one player."""

    command_points: int = 0
    tactical_vp: int = 0
    kill_vp: int = 0
    main_mission_vp: int = 0

    def __post_init__(self) -> None:
        _validate_range("command_points", self.command_points, CP_MIN, CP_MAX)
        _validate_range("tactical_vp", self.tactical_vp, VP_MIN, VP_MAX)
        _validate_range("kill_vp", self.kill_vp, VP_MIN, VP_MAX)
        _validate_range("main_mission_vp", self.main_mission_vp, VP_MIN, VP_MAX)

    def to_dict(self) -> dict[str, int]:
        return {
            "command_points": self.command_points,
            "tactical_vp": self.tactical_vp,
            "kill_vp": self.kill_vp,
            "main_mission_vp": self.main_mission_vp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> PlayerScores:
        return cls(
            command_points=data.get("command_points", 0),
            tactical_vp=data.get("tactical_vp", 0),
            kill_vp=data.get("kill_vp", 0),
            main_mission_vp=data.get("main_mission_vp", 0),
        )


@dataclass(slots=True)
class GameState:
    """Top-level V1 game state with stable serialization keys."""

    turning_point: int = 1
    player_one: PlayerScores = field(default_factory=PlayerScores)
    player_two: PlayerScores = field(default_factory=PlayerScores)

    def __post_init__(self) -> None:
        _validate_range("turning_point", self.turning_point, TURN_MIN, TURN_MAX)

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

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "turning_point": self.turning_point,
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

        try:
            schema_version = int(raw_schema_version)
        except (TypeError, ValueError) as exc:
            raise ValueError("schema_version must be an integer") from exc

        if schema_version != SCHEMA_VERSION:
            raise ValueError(
                f"unsupported schema_version: {schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )

        turning_point = int(data.get("turning_point", TURN_MIN))

        players_raw = data.get("players", {})
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
        )

    @classmethod
    def from_json(cls, payload: str) -> GameState:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError("JSON payload must decode to an object")
        return cls.from_dict(data)
