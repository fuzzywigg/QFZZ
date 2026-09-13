"""Corrupt JSON / schema / optional field edges for StateManager."""

import json
from pathlib import Path

import pytest

from qfzz.core.state import StateManager


def test_corrupt_playlist_raises_json_error(tmp_path: Path):
    sm = StateManager(honeycomb_dir=str(tmp_path))
    (tmp_path / "playlist.json").write_text("{not-json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        sm.get_playlist()


def test_deleted_current_track_returns_none(tmp_path: Path):
    sm = StateManager(honeycomb_dir=str(tmp_path))
    sm.set_current_track("t1", "Title", "Artist", genre="ambient", duration=10)
    (tmp_path / "current_track.json").unlink()
    assert sm.get_current_track() is None


def test_validate_schema_absent_and_none(tmp_path: Path):
    sm = StateManager(honeycomb_dir=str(tmp_path))
    assert sm._validate_schema({"a": 1}, "missing_schema") is True
    (tmp_path / "track_schema.json").write_text("{}", encoding="utf-8")
    assert sm._validate_schema(None, "track") is False
    assert sm._validate_schema({"ok": True}, "track") is True


def test_set_current_track_omits_optional_fields(tmp_path: Path):
    sm = StateManager(honeycomb_dir=str(tmp_path))
    sm.set_current_track("t2", "Only", "Artist")
    track = sm.get_current_track()
    assert track is not None
    assert "genre" not in track
    assert "duration" not in track
    assert track["title"] == "Only"


def test_add_task_preserves_custom_task_id(tmp_path: Path):
    sm = StateManager(honeycomb_dir=str(tmp_path))
    task_id = sm.add_task("scan", args={"path": "x"}, task_id="fixed-id")
    assert task_id == "fixed-id"
    tasks = sm.get_tasks()
    assert any(t["task_id"] == "fixed-id" for t in tasks["pending"])
