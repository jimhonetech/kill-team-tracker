"""Unit tests for StorageAdapter."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from app.state import GameState
from app.state.models import SCHEMA_VERSION
from app.storage.adapter import StorageAdapter


def test_save_writes_json_file(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)
    data: dict[str, object] = {"schema_version": SCHEMA_VERSION, "turning_point": 2}

    adapter.save_handler(data)

    save_file = tmp_path / "game_state.json"
    assert save_file.exists()
    written = json.loads(save_file.read_text(encoding="utf-8"))
    assert written == data


def test_resume_reads_json_file(tmp_path: Path) -> None:
    expected: dict[str, object] = {"schema_version": SCHEMA_VERSION, "turning_point": 3}
    save_file = tmp_path / "game_state.json"
    save_file.write_text(json.dumps(expected), encoding="utf-8")

    adapter = StorageAdapter(base_dir=tmp_path)
    result = adapter.resume_handler()

    assert result == expected


def test_resume_raises_on_missing_file(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)

    with pytest.raises(ValueError, match="No save file found"):
        adapter.resume_handler()


def test_save_creates_directory_if_missing(tmp_path: Path) -> None:
    nested = tmp_path / "deep" / "nested"
    adapter = StorageAdapter(base_dir=nested)
    data: dict[str, object] = {"schema_version": SCHEMA_VERSION, "turning_point": 1}

    adapter.save_handler(data)

    assert (nested / "game_state.json").exists()


def test_resume_raises_on_invalid_json(tmp_path: Path) -> None:
    save_file = tmp_path / "game_state.json"
    save_file.write_text("not valid json {{{", encoding="utf-8")

    adapter = StorageAdapter(base_dir=tmp_path)

    with pytest.raises(ValueError, match="invalid JSON"):
        adapter.resume_handler()


def test_save_and_resume_round_trip(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)
    data: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "turning_point": 4,
        "end_game": True,
        "selected_operation": "Recon Sweep",
        "players": {
            "player_one": {"command_points": 3, "secret_op": "tac_op"},
            "player_two": {"command_points": 1, "secret_op": "kill_op"},
        },
    }

    adapter.save_handler(data)
    result = adapter.resume_handler()

    assert result == data


def test_implicit_base_dir_resolves_lazily_after_app_starts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fallback_home = tmp_path / "fallback-home"
    android_data_dir = tmp_path / "android-data"
    monkeypatch.setattr(Path, "home", lambda: fallback_home)

    current_app: object | None = None

    class FakeApp:
        @classmethod
        def get_running_app(cls) -> object | None:
            return current_app

    fake_kivy_app = types.ModuleType("kivy.app")
    fake_kivy_app.App = FakeApp
    monkeypatch.setitem(sys.modules, "kivy.app", fake_kivy_app)

    adapter = StorageAdapter()

    class RunningApp:
        user_data_dir = str(android_data_dir)

    current_app = RunningApp()

    save_payload = {"schema_version": SCHEMA_VERSION, "turning_point": 2}
    history_payload = {
        "schema_version": SCHEMA_VERSION,
        "turning_point": 4,
        "end_game": True,
        "teams": {
            "player_one": "Kommandos",
            "player_two": "Kasrkin",
        },
        "players": {
            "player_one": {"tactical_vp": 5},
            "player_two": {"tactical_vp": 2},
        },
    }

    adapter.save_handler(save_payload)
    adapter.append_history_match(history_payload)

    assert (android_data_dir / "game_state.json").exists()
    assert (android_data_dir / "match_history.json").exists()
    assert adapter.resume_handler() == save_payload
    assert len(adapter.read_history_matches()) == 1
    assert not (fallback_home / ".killteamtracker").exists()


def test_history_append_creates_separate_history_file(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)
    active_payload = {"schema_version": SCHEMA_VERSION, "turning_point": 2}
    completed_payload = {
        "schema_version": SCHEMA_VERSION,
        "turning_point": 4,
        "end_game": True,
        "teams": {
            "player_one": "Kommandos",
            "player_two": "Kasrkin",
        },
        "players": {
            "player_one": {
                "tactical_vp": 5,
                "kill_vp": 1,
                "main_mission_vp": 2,
            },
            "player_two": {
                "tactical_vp": 2,
                "kill_vp": 1,
                "main_mission_vp": 1,
            },
        },
    }

    adapter.save_handler(active_payload)
    adapter.append_history_match(completed_payload)

    assert (tmp_path / "game_state.json").exists()
    assert (tmp_path / "match_history.json").exists()
    assert adapter.resume_handler() == active_payload

    matches = adapter.read_history_matches()
    assert len(matches) == 1
    assert matches[0]["winner"] == "player_one"
    assert (
        matches[0]["game_snapshot"] == GameState.from_dict(completed_payload).to_dict()
    )


def test_history_append_is_append_only(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)
    game_payload = {
        "schema_version": SCHEMA_VERSION,
        "turning_point": 4,
        "end_game": True,
        "teams": {
            "player_one": "Kommandos",
            "player_two": "Kasrkin",
        },
        "players": {
            "player_one": {"tactical_vp": 4},
            "player_two": {"tactical_vp": 3},
        },
    }

    adapter.append_history_match(game_payload)
    adapter.append_history_match(game_payload)

    matches = adapter.read_history_matches()
    assert len(matches) == 2


def test_read_history_matches_missing_file_returns_empty_list(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)

    assert adapter.read_history_matches() == []


def test_read_history_matches_invalid_json_raises(tmp_path: Path) -> None:
    history_file = tmp_path / "match_history.json"
    history_file.write_text("{invalid", encoding="utf-8")

    adapter = StorageAdapter(base_dir=tmp_path)

    with pytest.raises(ValueError, match="invalid JSON"):
        adapter.read_history_matches()


def test_read_win_rate_summary_handles_empty_and_non_empty_history(
    tmp_path: Path,
) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)

    empty_summary = adapter.read_stats_summary()
    assert empty_summary["total_matches"] == 0
    assert empty_summary["teams"] == {}
    assert empty_summary["primary_ops"]["combined"]["most_successful"]["op"] is None

    adapter.append_history_match(
        {
            "schema_version": SCHEMA_VERSION,
            "turning_point": 4,
            "end_game": True,
            "teams": {
                "player_one": "Kommandos",
                "player_two": "Kasrkin",
            },
            "players": {
                "player_one": {"tactical_vp": 6, "bonus_vp": 3, "secret_op": "tac_op"},
                "player_two": {"tactical_vp": 2, "secret_op": "kill_op"},
            },
        }
    )

    summary = adapter.read_stats_summary()
    assert summary["total_matches"] == 1
    assert summary["draws"] == 0
    assert summary["player_slots"]["player_one"]["wins"] == 1
    assert summary["teams"]["Kommandos"]["overall"]["wins"] == 1
    assert summary["primary_ops"]["player_one"]["most_successful"]["op"] == "tac_op"
    assert summary["op_buckets"]["tac_op"]["combined"]["selected_as_primary"] == 1

    compatibility_summary = adapter.read_win_rate_summary()
    assert compatibility_summary == summary
