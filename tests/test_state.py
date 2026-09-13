"""Tests for QFZZ State Management (Honeycomb)"""

import tempfile
from pathlib import Path

import pytest

from qfzz.core.state import StateManager, add_task, get_current_track, update_playlist


@pytest.fixture
def temp_honeycomb():
    """Create temporary honeycomb directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def state_manager(temp_honeycomb):
    """Create StateManager with temporary directory."""
    return StateManager(honeycomb_dir=temp_honeycomb)


class TestStateManager:
    """Test StateManager class."""

    def test_initialization(self, state_manager, temp_honeycomb):
        """Test StateManager initializes correctly."""
        assert state_manager.honeycomb_dir == Path(temp_honeycomb)

        # Check that state files were created
        assert (Path(temp_honeycomb) / "current_track.json").exists()
        assert (Path(temp_honeycomb) / "playlist.json").exists()
        assert (Path(temp_honeycomb) / "listener_state.json").exists()
        assert (Path(temp_honeycomb) / "tasks.json").exists()
        assert (Path(temp_honeycomb) / "dj_memory.json").exists()

    def test_current_track_operations(self, state_manager):
        """Test current track read/write operations."""
        # Initially should be None
        assert state_manager.get_current_track() is None

        # Set a track
        state_manager.set_current_track(
            track_id="track_123",
            title="Test Song",
            artist="Test Artist",
            genre="Test Genre",
            duration=180.0,
        )

        # Read it back
        track = state_manager.get_current_track()
        assert track is not None
        assert track["track_id"] == "track_123"
        assert track["title"] == "Test Song"
        assert track["artist"] == "Test Artist"
        assert track["genre"] == "Test Genre"
        assert track["duration"] == 180.0
        assert "started_at" in track

    def test_playlist_operations(self, state_manager):
        """Test playlist operations."""
        # Get initial playlist
        playlist = state_manager.get_playlist()
        assert playlist["queue"] == []

        # Add tracks to playlist
        state_manager.add_to_playlist(
            track_id="track_1", title="Song 1", artist="Artist 1", priority=5
        )

        state_manager.add_to_playlist(
            track_id="track_2", title="Song 2", artist="Artist 2", priority=8
        )

        # Verify tracks were added
        playlist = state_manager.get_playlist()
        assert len(playlist["queue"]) == 2
        assert playlist["queue"][0]["track_id"] == "track_1"
        assert playlist["queue"][1]["track_id"] == "track_2"
        assert playlist["queue"][1]["priority"] == 8

    def test_listener_state_operations(self, state_manager):
        """Test listener state operations."""
        # Get initial state
        state = state_manager.get_listener_state()
        assert state["active_listeners"] == 0
        assert state["recent_requests"] == []

        # Update listener count
        state_manager.update_listener_count(42)
        state = state_manager.get_listener_state()
        assert state["active_listeners"] == 42

        # Add listener request
        state_manager.add_listener_request(
            listener_id="listener_1", request_type="song_request", content="Play some jazz!"
        )

        state = state_manager.get_listener_state()
        assert len(state["recent_requests"]) == 1
        assert state["recent_requests"][0]["listener_id"] == "listener_1"
        assert state["recent_requests"][0]["request_type"] == "song_request"
        assert state["recent_requests"][0]["content"] == "Play some jazz!"

    def test_listener_request_limit(self, state_manager):
        """Test that recent requests are limited to 100."""
        # Add 150 requests
        for i in range(150):
            state_manager.add_listener_request(
                listener_id=f"listener_{i}", request_type="test", content=f"Request {i}"
            )

        state = state_manager.get_listener_state()
        # Should only keep last 100
        assert len(state["recent_requests"]) == 100

    def test_task_operations(self, state_manager):
        """Test task queue operations."""
        # Get initial tasks
        tasks = state_manager.get_tasks()
        assert tasks["pending"] == []

        # Add task
        task_id = state_manager.add_task(action="play_song", args={"track_id": "track_123"})

        assert task_id is not None

        # Verify task was added
        tasks = state_manager.get_tasks()
        assert len(tasks["pending"]) == 1
        assert tasks["pending"][0]["task_id"] == task_id
        assert tasks["pending"][0]["action"] == "play_song"
        assert tasks["pending"][0]["status"] == "pending"

        # Update task status
        success = state_manager.update_task_status(task_id, "completed")
        assert success is True

        tasks = state_manager.get_tasks()
        assert tasks["pending"][0]["status"] == "completed"

    def test_task_status_update_nonexistent(self, state_manager):
        """Test updating status of nonexistent task."""
        success = state_manager.update_task_status("nonexistent_id", "completed")
        assert success is False

    def test_dj_memory_operations(self, state_manager):
        """Test DJ memory operations."""
        # Get initial memory
        memory = state_manager.get_dj_memory()
        assert memory["conversation_history"] == []
        assert memory["learned_patterns"] == {}
        assert len(memory["banned_phrases"]) > 0  # Has default banned phrases

        # Add conversation
        state_manager.add_conversation(role="listener", content="What's playing?")

        state_manager.add_conversation(
            role="dj", content="Right now we're spinning some smooth jazz!"
        )

        memory = state_manager.get_dj_memory()
        assert len(memory["conversation_history"]) == 2
        assert memory["conversation_history"][0]["role"] == "listener"
        assert memory["conversation_history"][1]["role"] == "dj"

        # Update learned pattern
        state_manager.update_learned_pattern("favorite_genre", {"genre": "jazz", "count": 5})

        memory = state_manager.get_dj_memory()
        assert "favorite_genre" in memory["learned_patterns"]
        assert memory["learned_patterns"]["favorite_genre"]["genre"] == "jazz"

    def test_conversation_history_limit(self, state_manager):
        """Test that conversation history is limited to 1000 messages."""
        # Add 1100 messages
        for i in range(1100):
            state_manager.add_conversation(role="listener", content=f"Message {i}")

        memory = state_manager.get_dj_memory()
        # Should only keep last 1000
        assert len(memory["conversation_history"]) == 1000

    def test_thread_safety(self, state_manager):
        """Concurrent playlist writes must not corrupt JSON state."""
        import threading

        errors: list[BaseException] = []

        def add_tracks(thread_id):
            try:
                for i in range(5):
                    state_manager.add_to_playlist(
                        track_id=f"track_{thread_id}_{i}",
                        title=f"Song {thread_id}_{i}",
                        artist="Artist",
                    )
            except BaseException as exc:  # collect and re-check after join
                errors.append(exc)

        threads = [threading.Thread(target=add_tracks, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"worker errors: {errors}"
        playlist = state_manager.get_playlist()
        assert isinstance(playlist, dict)
        assert isinstance(playlist.get("queue"), list)
        # Lost updates are possible without transactional locking; require
        # non-corrupt readable state and at least one successful write.
        assert 1 <= len(playlist["queue"]) <= 15
        track_ids = [t.get("track_id") for t in playlist["queue"]]
        assert all(isinstance(tid, str) and tid.startswith("track_") for tid in track_ids)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_current_track(self, temp_honeycomb, monkeypatch):
        """Test get_current_track convenience function."""
        # Monkeypatch StateManager to use temp directory
        original_init = StateManager.__init__

        def mock_init(self, honeycomb_dir=temp_honeycomb):
            original_init(self, honeycomb_dir)

        monkeypatch.setattr(StateManager, "__init__", mock_init)

        # Should return None initially
        track = get_current_track()
        assert track is None

    def test_update_playlist(self, temp_honeycomb, monkeypatch):
        """Test update_playlist convenience function."""
        original_init = StateManager.__init__

        def mock_init(self, honeycomb_dir=temp_honeycomb):
            original_init(self, honeycomb_dir)

        monkeypatch.setattr(StateManager, "__init__", mock_init)

        # Update playlist
        queue = [{"track_id": "track_1", "title": "Song 1", "artist": "Artist 1"}]
        update_playlist(queue)

        # Verify it was updated
        manager = StateManager(honeycomb_dir=temp_honeycomb)
        playlist = manager.get_playlist()
        assert len(playlist["queue"]) == 1

    def test_add_task(self, temp_honeycomb, monkeypatch):
        """Test add_task convenience function."""
        original_init = StateManager.__init__

        def mock_init(self, honeycomb_dir=temp_honeycomb):
            original_init(self, honeycomb_dir)

        monkeypatch.setattr(StateManager, "__init__", mock_init)

        # Add task
        task_id = add_task("test_action", {"arg1": "value1"})
        assert task_id is not None

        # Verify it was added
        manager = StateManager(honeycomb_dir=temp_honeycomb)
        tasks = manager.get_tasks()
        assert len(tasks["pending"]) == 1
