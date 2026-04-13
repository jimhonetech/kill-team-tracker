"""End-to-end persistence tests using real file I/O via StorageAdapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.state import GameState, PlayerScores
from app.storage.adapter import StorageAdapter


def test_e2e_save_resume_round_trip_with_real_file_io(tmp_path: Path) -> None:
    state = GameState(
        turning_point=3,
        player_one=PlayerScores(command_points=2, tactical_vp=4, kill_vp=1),
        player_two=PlayerScores(command_points=1, main_mission_vp=5, bonus_vp=2),
        selected_operation="Secure Objective",
    )
    adapter = StorageAdapter(base_dir=tmp_path)

    expected = json.loads(state.to_json())
    adapter.save_handler(expected)
    resumed = adapter.resume_handler()

    assert resumed == expected


def test_e2e_resume_from_corrupt_file_raises_value_error(tmp_path: Path) -> None:
    save_file = tmp_path / "game_state.json"
    save_file.write_text("{ not valid json", encoding="utf-8")
    adapter = StorageAdapter(base_dir=tmp_path)

    with pytest.raises(ValueError):
        adapter.resume_handler()


def test_e2e_resume_missing_file_raises_value_error(tmp_path: Path) -> None:
    adapter = StorageAdapter(base_dir=tmp_path)

    with pytest.raises(ValueError):
        adapter.resume_handler()
