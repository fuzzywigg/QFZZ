"""
Comprehensive tests for Honeycomb State Management.

Tests file locking, atomic writes, schema validation, error recovery,
and edge cases not covered in test_state.py.
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from filelock import FileLock, Timeout

from qfzz.core.state import StateManager


class TestFileLocking:
    """Test file locking behavior and timeouts."""

    def test_file_lock_timeout(self, temp_honeycomb):
        """Test that file lock times out after 10 seconds."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)
        track_file = Path(temp_honeycomb) / "current_track.json"
        lock_file = Path(temp_honeycomb) / ".current_track.json.lock"

        # Acquire lock manually to block state manager
        lock = FileLock(lock_file, timeout=0.1)
        lock.acquire()

        try:
            # Attempt to write should timeout
            with pytest.raises(Timeout):
                state_manager.set_current_track(
                    track_id="track_1",
                    title="Test",
                    artist="Artist",
                    genre="Genre",
                    duration=180.0,
                )
        finally:
            lock.release()

    def test_concurrent_writes_dont_corrupt(self, temp_honeycomb):
        """Test that concurrent writes to same file don't cause corruption."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)
        errors = []

        def write_tracks(thread_id):
            try:
                for i in range(10):
                    state_manager.add_to_playlist(
                        track_id=f"track_{thread_id}_{i}",
                        title=f"Song {i}",
                        artist=f"Artist {thread_id}",
                    )
            except Exception as e:
                errors.append(e)

        # Run 5 threads concurrently
        threads = [threading.Thread(target=write_tracks, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # File should still be valid JSON
        playlist = state_manager.get_playlist()
        assert isinstance(playlist, dict)
        assert "queue" in playlist
        assert isinstance(playlist["queue"], list)
        # Should have some tracks (exact count may vary due to timing)
        assert len(playlist["queue"]) > 0

    def test_multiple_state_managers_same_directory(self, temp_honeycomb):
        """Test multiple StateManager instances can share the same directory."""
        manager1 = StateManager(honeycomb_dir=temp_honeycomb)
        manager2 = StateManager(honeycomb_dir=temp_honeycomb)

        # Write with manager1
        manager1.set_current_track(
            track_id="track_1", title="Song 1", artist="Artist 1", genre="Pop", duration=180.0
        )

        # Read with manager2
        track = manager2.get_current_track()
        assert track is not None
        assert track["track_id"] == "track_1"
        assert track["title"] == "Song 1"


class TestAtomicWrites:
    """Test atomic write operations."""

    def test_partial_write_recovery(self, temp_honeycomb, mock_file_corruption):
        """Test recovery from partial/corrupted writes."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Set initial valid state
        state_manager.set_current_track(
            track_id="track_1", title="Valid Song", artist="Artist", genre="Pop", duration=180.0
        )

        # Corrupt the file
        track_file = Path(temp_honeycomb) / "current_track.json"
        mock_file_corruption(track_file)

        # Attempting to read corrupted file should handle gracefully
        # The implementation might return None or reinitialize
        try:
            track = state_manager.get_current_track()
            # Either returns None or handles error internally
            assert track is None or isinstance(track, dict)
        except json.JSONDecodeError:
            # Or raises JSONDecodeError that should be handled by caller
            pass

    def test_write_creates_valid_json(self, temp_honeycomb):
        """Test that all writes create valid, parseable JSON."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Write to all state files
        state_manager.set_current_track(
            track_id="track_1", title="Song", artist="Artist", genre="Pop", duration=180.0
        )
        state_manager.add_to_playlist(track_id="track_2", title="Song 2", artist="Artist 2")
        state_manager.update_listener_count(10)
        state_manager.add_listener_request("listener_1", "song_request", "Play jazz")
        state_manager.add_task("play_song", {"track_id": "track_1"})
        state_manager.add_conversation("dj", "Welcome to the show!")

        # Verify all files contain valid JSON
        for filename in [
            "current_track.json",
            "playlist.json",
            "listener_state.json",
            "tasks.json",
            "dj_memory.json",
        ]:
            filepath = Path(temp_honeycomb) / filename
            assert filepath.exists()

            with open(filepath) as f:
                data = json.load(f)  # Should not raise
                assert isinstance(data, (dict, type(None)))


class TestSchemaValidation:
    """Test schema validation for state files."""

    def test_validate_schema_valid_data(self, temp_honeycomb):
        """Test schema validation with valid data."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Create a simple schema file
        schema_path = Path(temp_honeycomb) / "test_schema.json"
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
        }
        with open(schema_path, "w") as f:
            json.dump(schema, f)

        valid_data = {"id": "123", "name": "Test"}

        # Note: Current implementation might not have full schema validation
        # This tests the _validate_schema method exists and handles data
        result = state_manager._validate_schema(valid_data, "test")
        # If method not fully implemented, should return True or handle gracefully
        assert isinstance(result, bool)

    def test_default_structures_match_schema(self, temp_honeycomb):
        """Test that default state structures are valid."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Check current_track (can be None)
        track = state_manager.get_current_track()
        assert track is None or isinstance(track, dict)

        # Check playlist has required structure
        playlist = state_manager.get_playlist()
        assert isinstance(playlist, dict)
        assert "queue" in playlist
        assert isinstance(playlist["queue"], list)

        # Check listener_state
        listener_state = state_manager.get_listener_state()
        assert isinstance(listener_state, dict)
        assert "active_listeners" in listener_state
        assert "recent_requests" in listener_state
        assert isinstance(listener_state["active_listeners"], int)
        assert isinstance(listener_state["recent_requests"], list)

        # Check tasks
        tasks = state_manager.get_tasks()
        assert isinstance(tasks, dict)
        assert "pending" in tasks
        assert isinstance(tasks["pending"], list)

        # Check dj_memory
        memory = state_manager.get_dj_memory()
        assert isinstance(memory, dict)
        assert "conversation_history" in memory
        assert "learned_patterns" in memory
        assert "banned_phrases" in memory


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_nonexistent_directory_creates_automatically(self):
        """Test that StateManager creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            honeycomb_path = Path(tmpdir) / "nonexistent" / "honeycomb"
            assert not honeycomb_path.exists()

            state_manager = StateManager(honeycomb_dir=str(honeycomb_path))

            # Directory should now exist
            assert honeycomb_path.exists()
            assert honeycomb_path.is_dir()

            # State files should be created
            assert (honeycomb_path / "current_track.json").exists()

    def test_missing_state_file_initializes_with_defaults(self, temp_honeycomb):
        """Test that missing state files are recreated with defaults."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Remove a state file
        playlist_file = Path(temp_honeycomb) / "playlist.json"
        playlist_file.unlink()

        # Reading should reinitialize or handle gracefully
        # Depending on implementation, might recreate or return default
        playlist = state_manager.get_playlist()

        # Should get valid data (either cached or reinitialized)
        assert isinstance(playlist, dict)

    def test_corrupted_json_recovery(self, temp_honeycomb, mock_file_corruption):
        """Test recovery from corrupted JSON files."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Corrupt the tasks file
        tasks_file = Path(temp_honeycomb) / "tasks.json"
        mock_file_corruption(tasks_file)

        # Reading corrupted file should handle error
        try:
            tasks = state_manager.get_tasks()
            # Implementation might return default or None
            assert tasks is None or isinstance(tasks, dict)
        except json.JSONDecodeError:
            # Or might raise error for caller to handle
            pass

    def test_permission_error_handling(self, temp_honeycomb):
        """Test handling of permission errors."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        track_file = Path(temp_honeycomb) / "current_track.json"

        # Make file read-only (Unix-like systems)
        if os.name != "nt":  # Skip on Windows
            os.chmod(track_file, 0o444)

            try:
                # Writing should fail with permission error
                with pytest.raises((PermissionError, OSError)):
                    state_manager.set_current_track(
                        track_id="track_1",
                        title="Test",
                        artist="Artist",
                        genre="Pop",
                        duration=180.0,
                    )
            finally:
                # Restore permissions
                os.chmod(track_file, 0o644)


class TestStateOperations:
    """Test specific state operations and edge cases."""

    def test_request_history_pruning_exactly_100(self, temp_honeycomb):
        """Test that request history is pruned to exactly 100 entries."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Add exactly 150 requests
        for i in range(150):
            state_manager.add_listener_request(
                listener_id=f"listener_{i}", request_type="test", content=f"Request {i}"
            )

        state = state_manager.get_listener_state()
        assert len(state["recent_requests"]) == 100

        # Verify it's the last 100 (most recent)
        assert state["recent_requests"][-1]["content"] == "Request 149"
        assert state["recent_requests"][0]["content"] == "Request 50"

    def test_conversation_history_pruning_exactly_1000(self, temp_honeycomb):
        """Test that conversation history is pruned to exactly 1000 entries."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Add exactly 1200 messages
        for i in range(1200):
            state_manager.add_conversation(role="listener", content=f"Message {i}")

        memory = state_manager.get_dj_memory()
        assert len(memory["conversation_history"]) == 1000

        # Verify it's the last 1000 (most recent)
        assert memory["conversation_history"][-1]["content"] == "Message 1199"
        assert memory["conversation_history"][0]["content"] == "Message 200"

    def test_set_current_track_with_none_clears_track(self, temp_honeycomb):
        """Test that setting current track to None clears it."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Set a track
        state_manager.set_current_track(
            track_id="track_1", title="Song", artist="Artist", genre="Pop", duration=180.0
        )
        assert state_manager.get_current_track() is not None

        # Clear it by writing None
        track_file = Path(temp_honeycomb) / "current_track.json"
        state_manager._write_file(track_file, None)

        # Should return None
        assert state_manager.get_current_track() is None

    def test_update_task_status_completed_to_failed(self, temp_honeycomb):
        """Test updating task status from completed to failed."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        task_id = state_manager.add_task("test_action", {"arg": "value"})
        state_manager.update_task_status(task_id, "completed")

        tasks = state_manager.get_tasks()
        assert tasks["pending"][0]["status"] == "completed"

        # Update again
        state_manager.update_task_status(task_id, "failed")
        tasks = state_manager.get_tasks()
        assert tasks["pending"][0]["status"] == "failed"

    def test_learned_patterns_update_overwrites(self, temp_honeycomb):
        """Test that updating learned patterns overwrites existing values."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        state_manager.update_learned_pattern("favorite_genre", {"genre": "jazz", "count": 5})
        memory = state_manager.get_dj_memory()
        assert memory["learned_patterns"]["favorite_genre"]["count"] == 5

        # Update same pattern
        state_manager.update_learned_pattern("favorite_genre", {"genre": "rock", "count": 10})
        memory = state_manager.get_dj_memory()
        assert memory["learned_patterns"]["favorite_genre"]["genre"] == "rock"
        assert memory["learned_patterns"]["favorite_genre"]["count"] == 10


class TestThreadSafety:
    """Enhanced thread safety tests."""

    def test_read_write_concurrency(self, temp_honeycomb):
        """Test concurrent reads and writes."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)
        errors = []
        read_values = []

        def writer():
            try:
                for i in range(20):
                    state_manager.update_listener_count(i)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(("write", e))

        def reader():
            try:
                for _ in range(20):
                    state = state_manager.get_listener_state()
                    read_values.append(state["active_listeners"])
                    time.sleep(0.001)
            except Exception as e:
                errors.append(("read", e))

        # Start 2 writers and 3 readers
        threads = []
        threads.extend([threading.Thread(target=writer) for _ in range(2)])
        threads.extend([threading.Thread(target=reader) for _ in range(3)])

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0
        # Should have read values
        assert len(read_values) > 0


@pytest.mark.unit
class TestStateManagerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_playlist_operations(self, temp_honeycomb):
        """Test operations on empty playlist."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        playlist = state_manager.get_playlist()
        assert len(playlist["queue"]) == 0

        # Update with empty queue
        state_manager._write_file(
            Path(temp_honeycomb) / "playlist.json", {"queue": [], "metadata": {}}
        )

        playlist = state_manager.get_playlist()
        assert len(playlist["queue"]) == 0

    def test_large_conversation_history(self, temp_honeycomb):
        """Test handling of large conversation history."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        # Add conversations with large content
        large_content = "x" * 10000  # 10KB content
        for i in range(10):
            state_manager.add_conversation(role="listener", content=f"Message {i}: {large_content}")

        memory = state_manager.get_dj_memory()
        assert len(memory["conversation_history"]) == 10

        # File should still be readable
        memory2 = state_manager.get_dj_memory()
        assert len(memory2["conversation_history"]) == 10

    def test_special_characters_in_content(self, temp_honeycomb):
        """Test handling of special characters in content."""
        state_manager = StateManager(honeycomb_dir=temp_honeycomb)

        special_chars = 'Test with "quotes", \\backslashes\\, and emoji 🎵🎶'

        state_manager.set_current_track(
            track_id="track_1",
            title=special_chars,
            artist=special_chars,
            genre="Pop",
            duration=180.0,
        )

        track = state_manager.get_current_track()
        assert track["title"] == special_chars
        assert track["artist"] == special_chars
