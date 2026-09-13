"""StateManager restores defaults when honeycomb JSON files are deleted."""

from pathlib import Path

from qfzz.core.state import StateManager


def test_add_to_playlist_after_playlist_file_deleted(temp_honeycomb):
    mgr = StateManager(honeycomb_dir=temp_honeycomb)
    Path(temp_honeycomb, "playlist.json").unlink()

    mgr.add_to_playlist("t1", "Song", "Artist", priority=3)
    playlist = mgr.get_playlist()
    assert len(playlist["queue"]) == 1
    assert playlist["queue"][0]["track_id"] == "t1"
    assert Path(temp_honeycomb, "playlist.json").exists()


def test_listener_and_task_mutations_after_files_deleted(temp_honeycomb):
    mgr = StateManager(honeycomb_dir=temp_honeycomb)
    Path(temp_honeycomb, "listener_state.json").unlink()
    Path(temp_honeycomb, "tasks.json").unlink()

    mgr.update_listener_count(4)
    assert mgr.get_listener_state()["active_listeners"] == 4

    mgr.add_listener_request("L1", "song_request", "play jazz")
    assert len(mgr.get_listener_state()["recent_requests"]) == 1

    task_id = mgr.add_task("scan", {"path": "/tmp"})
    assert task_id.startswith("task_")
    assert len(mgr.get_tasks()["pending"]) == 1
    assert mgr.update_task_status(task_id, "completed") is True


def test_dj_memory_mutations_after_file_deleted(temp_honeycomb):
    mgr = StateManager(honeycomb_dir=temp_honeycomb)
    Path(temp_honeycomb, "dj_memory.json").unlink()

    mgr.add_conversation("listener", "hello")
    memory = mgr.get_dj_memory()
    assert len(memory["conversation_history"]) == 1
    assert "banned_phrases" in memory

    mgr.update_learned_pattern("mood", {"chill": 0.8})
    assert mgr.get_dj_memory()["learned_patterns"]["mood"]["chill"] == 0.8
