"""Unit tests for StorageAdapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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
