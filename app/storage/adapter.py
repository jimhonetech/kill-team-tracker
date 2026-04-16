"""File-backed JSON storage adapter for Kill Team Tracker."""

from __future__ import annotations

import json
from pathlib import Path

from app.state import (
    CompletedMatchArchive,
    GameState,
    build_stats_summary,
    load_archives_from_payload,
    migrate_history_payload,
)


def _get_base_dir() -> Path:
    """Return the base directory for save data.

    On Android (Kivy available and running), use App.user_data_dir.
    On desktop or CI, use ~/.killteamtracker.
    """
    try:
        from kivy.app import App  # type: ignore[import-untyped]

        app = App.get_running_app()
        if app is not None:
            return Path(app.user_data_dir)
    except Exception:
        pass

    return Path.home() / ".killteamtracker"


_SAVE_FILENAME = "game_state.json"
_HISTORY_FILENAME = "match_history.json"


class StorageAdapter:
    """Provides save/resume handlers backed by a local JSON file."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._configured_base_dir = base_dir

    def _base_dir(self) -> Path:
        if self._configured_base_dir is not None:
            return self._configured_base_dir
        return _get_base_dir()

    def _save_path(self) -> Path:
        return self._base_dir() / _SAVE_FILENAME

    def _history_path(self) -> Path:
        return self._base_dir() / _HISTORY_FILENAME

    def save_handler(self, data: dict[str, object]) -> None:
        """Serialize *data* as JSON and write it to the save file."""
        self._base_dir().mkdir(parents=True, exist_ok=True)
        save_path = self._save_path()
        save_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")

    def resume_handler(self) -> dict[str, object]:
        """Read the save file and return the decoded dict.

        Raises:
            ValueError: if the save file does not exist or contains invalid JSON.
        """
        save_path = self._save_path()
        try:
            text = save_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise ValueError(
                f"No save file found at {save_path}. "
                "Start a new game before resuming."
            ) from exc

        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Save file at {save_path} contains invalid JSON: {exc}"
            ) from exc

        if not isinstance(result, dict):
            raise ValueError(
                f"Save file at {save_path} does not contain a JSON object."
            )

        return result  # type: ignore[return-value]

    def append_history_match(self, game_data: dict[str, object]) -> dict[str, object]:
        """Append one completed match archive into match history storage."""
        state = GameState.from_dict(game_data)
        archive = CompletedMatchArchive.from_game_state(state)

        self._base_dir().mkdir(parents=True, exist_ok=True)
        history_payload = self._read_history_payload()
        matches = history_payload["matches"]
        assert isinstance(matches, list)
        matches.append(archive.to_dict())
        history_path = self._history_path()
        history_path.write_text(
            json.dumps(history_payload, sort_keys=True),
            encoding="utf-8",
        )
        return archive.to_dict()

    def read_history_matches(self) -> list[dict[str, object]]:
        """Return canonical archived matches from history storage."""
        payload = self._read_history_payload()
        matches = payload["matches"]
        assert isinstance(matches, list)
        return matches

    def read_win_rate_summary(self) -> dict[str, object]:
        """Return the compatibility stats summary from history storage."""
        return self.read_stats_summary()

    def read_stats_summary(self) -> dict[str, object]:
        """Return the full stats read model from history storage."""
        history_path = self._history_path()
        if not history_path.exists():
            return build_stats_summary([])

        payload = self._read_history_json(history_path)
        archives = load_archives_from_payload(payload)
        return build_stats_summary(archives)

    def _read_history_json(self, history_path: Path) -> object:
        try:
            text = history_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"History file at {history_path} contains invalid JSON: {exc}"
            ) from exc

    def _read_history_payload(self) -> dict[str, object]:
        history_path = self._history_path()
        payload = self._read_history_json(history_path)
        try:
            return migrate_history_payload(payload)
        except ValueError as exc:
            raise ValueError(f"Invalid history file at {history_path}: {exc}") from exc
