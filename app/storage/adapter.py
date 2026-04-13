"""File-backed JSON storage adapter for Kill Team Tracker."""

from __future__ import annotations

import json
from pathlib import Path


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


class StorageAdapter:
    """Provides save/resume handlers backed by a local JSON file."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir if base_dir is not None else _get_base_dir()

    def _save_path(self) -> Path:
        return self._base_dir / _SAVE_FILENAME

    def save_handler(self, data: dict[str, object]) -> None:
        """Serialize *data* as JSON and write it to the save file."""
        self._base_dir.mkdir(parents=True, exist_ok=True)
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
