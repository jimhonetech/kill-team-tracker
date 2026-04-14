"""Shared player color palette for consistent UI styling."""

from __future__ import annotations

PlayerColor = tuple[float, float, float, float]

PLAYER_PALETTE: dict[str, dict[str, PlayerColor]] = {
    "player_one": {
        "accent": (0.15, 0.42, 0.72, 1),
        "surface": (0.83, 0.9, 0.98, 1),
        "surface_selected": (0.26, 0.56, 0.86, 1),
    },
    "player_two": {
        "accent": (0.78, 0.34, 0.17, 1),
        "surface": (0.99, 0.9, 0.84, 1),
        "surface_selected": (0.9, 0.47, 0.25, 1),
    },
}

BUTTON_TEXT_DARK: PlayerColor = (0.12, 0.14, 0.18, 1)
BUTTON_TEXT_LIGHT: PlayerColor = (1, 1, 1, 1)
NEUTRAL_TEXT: PlayerColor = (0.18, 0.18, 0.18, 1)


def player_accent(player: str) -> PlayerColor:
    return PLAYER_PALETTE[player]["accent"]


def player_surface(player: str) -> PlayerColor:
    return PLAYER_PALETTE[player]["surface"]


def player_surface_selected(player: str) -> PlayerColor:
    return PLAYER_PALETTE[player]["surface_selected"]


def player_button_text(selected: bool) -> PlayerColor:
    return BUTTON_TEXT_LIGHT if selected else BUTTON_TEXT_DARK
