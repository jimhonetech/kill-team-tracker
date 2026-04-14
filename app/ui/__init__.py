"""UI components for Kill Team Tracker."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .main_screen import MainGameScreen

if TYPE_CHECKING:
    from .flow import HomeScreen, TeamSelectionScreen, TrackerFlow


__all__ = [
    "HomeScreen",
    "MainGameScreen",
    "TeamSelectionScreen",
    "TrackerFlow",
]


def __getattr__(name: str) -> Any:
    if name in {"HomeScreen", "TeamSelectionScreen", "TrackerFlow"}:
        from . import flow

        return getattr(flow, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
