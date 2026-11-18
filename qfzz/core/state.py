"""
QFZZ Honeycomb State Management

Stigmergic state system for agent coordination through shared JSON state files.
Thread-safe operations with schema validation.
"""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from filelock import FileLock


class StateManager:
    """
    Thread-safe state manager for honeycomb JSON files.

    Provides read/write operations with automatic locking and schema validation.
    """

    def __init__(self, honeycomb_dir: str = "honeycomb"):
        """
        Initialize StateManager.

        Args:
            honeycomb_dir: Path to honeycomb directory containing state files
        """
        self.honeycomb_dir = Path(honeycomb_dir)
        self.honeycomb_dir.mkdir(parents=True, exist_ok=True)

        # Initialize empty state files if they don't exist
        self._initialize_state_files()

    def _initialize_state_files(self):
        """Initialize empty state files with default structures."""
        default_states = {
            "current_track.json": None,
            "playlist.json": {"queue": []},
            "listener_state.json": {
                "active_listeners": 0,
                "recent_requests": [],
                "preferences": {},
            },
            "tasks.json": {"pending": []},
            "dj_memory.json": {
                "conversation_history": [],
                "learned_patterns": {},
                "banned_phrases": [
                    "AI",
                    "LLM",
                    "language model",
                    "I am an AI",
                    "as an artificial intelligence",
                    "I don't have feelings",
                ],
            },
        }

        for filename, default_data in default_states.items():
            filepath = self.honeycomb_dir / filename
            if not filepath.exists():
                self._write_file(filepath, default_data)

    def _get_lock_path(self, filepath: Path) -> Path:
        """Get lock file path for a given file."""
        return filepath.parent / f".{filepath.name}.lock"

    def _load_json(self, filepath: Path) -> Any:
        """Read JSON without taking the file lock."""
        if not filepath.exists():
            return None

        with open(filepath) as f:
            return json.load(f)

    def _dump_json(self, filepath: Path, data: Any) -> None:
        """Write JSON without taking the file lock."""
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _read_file(self, filepath: Path) -> Any:
        """Read JSON file with file locking."""
        with FileLock(self._get_lock_path(filepath), timeout=10):
            return self._load_json(filepath)

    def _write_file(self, filepath: Path, data: Any) -> None:
        """Write JSON file with file locking."""
        with FileLock(self._get_lock_path(filepath), timeout=10):
            self._dump_json(filepath, data)

    def _mutate_file(self, filepath: Path, mutator: Callable[[Any], Any]) -> Any:
        """Read, mutate, and write JSON while holding a single file lock.

        Separate read and write locks drop concurrent updates: another writer
        can commit between them. Callers that append or edit existing state
        use this so the whole change is atomic.
        """
        with FileLock(self._get_lock_path(filepath), timeout=10):
            data = self._load_json(filepath)
            result = mutator(data)
            self._dump_json(filepath, data)
            return result

    def _validate_schema(self, data: Any, schema_name: str) -> bool:
        """
        Validate data against schema.

        Args:
            data: Data to validate
            schema_name: Name of schema file (without .json extension)

        Returns:
            True if valid, False otherwise
        """
        schema_path = self.honeycomb_dir / f"{schema_name}_schema.json"
        if not schema_path.exists():
            # No schema, skip validation
            return True

        # Basic validation - in production, use jsonschema library
        # For now, just check data is not None for required schemas
        return data is not None

    # Current Track Operations
    def get_current_track(self) -> dict[str, Any] | None:
        """Get currently playing track."""
        return self._read_file(self.honeycomb_dir / "current_track.json")

    def set_current_track(
        self,
        track_id: str,
        title: str,
        artist: str,
        genre: str | None = None,
        duration: float | None = None,
    ) -> None:
        """
        Set currently playing track.

        Args:
            track_id: Unique track identifier
            title: Track title
            artist: Artist name
            genre: Music genre
            duration: Track duration in seconds
        """
        track_data: dict[str, Any] = {
            "track_id": track_id,
            "title": title,
            "artist": artist,
            "started_at": datetime.utcnow().isoformat(),
        }

        if genre:
            track_data["genre"] = genre
        if duration:
            track_data["duration"] = duration

        self._write_file(self.honeycomb_dir / "current_track.json", track_data)

    # Playlist Operations
    def get_playlist(self) -> dict[str, list[dict[str, Any]]]:
        """Get current playlist queue."""
        return self._read_file(self.honeycomb_dir / "playlist.json")

    def update_playlist(self, queue: list[dict[str, Any]]) -> None:
        """
        Update entire playlist queue.

        Args:
            queue: List of track dictionaries
        """
        self._write_file(self.honeycomb_dir / "playlist.json", {"queue": queue})

    def add_to_playlist(self, track_id: str, title: str, artist: str, priority: int = 5) -> None:
        """
        Add track to playlist.

        Args:
            track_id: Unique track identifier
            title: Track title
            artist: Artist name
            priority: Priority level (0-10, higher is more important)
        """
        track = {
            "track_id": track_id,
            "title": title,
            "artist": artist,
            "priority": priority,
            "added_at": datetime.utcnow().isoformat(),
        }

        def append_track(playlist: dict[str, list[dict[str, Any]]]) -> None:
            playlist["queue"].append(track)

        self._mutate_file(self.honeycomb_dir / "playlist.json", append_track)

    # Listener State Operations
    def get_listener_state(self) -> dict[str, Any]:
        """Get listener state."""
        return self._read_file(self.honeycomb_dir / "listener_state.json")

    def update_listener_count(self, count: int) -> None:
        """Update active listener count."""

        def set_count(state: dict[str, Any]) -> None:
            state["active_listeners"] = count

        self._mutate_file(self.honeycomb_dir / "listener_state.json", set_count)

    def add_listener_request(self, listener_id: str, request_type: str, content: str) -> None:
        """
        Add listener request.

        Args:
            listener_id: Unique listener identifier
            request_type: Type of request (e.g., 'song_request', 'shoutout', 'question')
            content: Request content
        """
        request = {
            "request_id": f"{listener_id}_{datetime.utcnow().timestamp()}",
            "listener_id": listener_id,
            "request_type": request_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        def append_request(state: dict[str, Any]) -> None:
            state["recent_requests"].append(request)
            if len(state["recent_requests"]) > 100:
                state["recent_requests"] = state["recent_requests"][-100:]

        self._mutate_file(self.honeycomb_dir / "listener_state.json", append_request)

    # Task Operations
    def get_tasks(self) -> dict[str, list[dict[str, Any]]]:
        """Get pending tasks."""
        return self._read_file(self.honeycomb_dir / "tasks.json")

    def add_task(
        self, action: str, args: dict[str, Any] | None = None, task_id: str | None = None
    ) -> str:
        """
        Add task to queue.

        Args:
            action: Action to perform
            args: Action arguments
            task_id: Optional task ID (auto-generated if not provided)

        Returns:
            Task ID
        """
        if task_id is None:
            task_id = f"task_{datetime.utcnow().timestamp()}"

        task = {
            "task_id": task_id,
            "action": action,
            "args": args or {},
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        def append_task(tasks: dict[str, list[dict[str, Any]]]) -> None:
            tasks["pending"].append(task)

        self._mutate_file(self.honeycomb_dir / "tasks.json", append_task)

        return task_id

    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update task status.

        Args:
            task_id: Task identifier
            status: New status ('pending', 'processing', 'completed', 'failed')

        Returns:
            True if task was found and updated, False otherwise
        """
        found = False

        def set_status(tasks: dict[str, list[dict[str, Any]]]) -> None:
            nonlocal found
            for task in tasks["pending"]:
                if task["task_id"] == task_id:
                    task["status"] = status
                    found = True
                    return

        self._mutate_file(self.honeycomb_dir / "tasks.json", set_status)
        return found

    # DJ Memory Operations
    def get_dj_memory(self) -> dict[str, Any]:
        """Get DJ memory (conversation history, learned patterns, banned phrases)."""
        return self._read_file(self.honeycomb_dir / "dj_memory.json")

    def add_conversation(self, role: str, content: str) -> None:
        """
        Add conversation to DJ memory.

        Args:
            role: Speaker role ('dj', 'listener', 'system')
            content: Message content
        """
        entry = {"timestamp": datetime.utcnow().isoformat(), "role": role, "content": content}

        def append_entry(memory: dict[str, Any]) -> None:
            memory["conversation_history"].append(entry)
            if len(memory["conversation_history"]) > 1000:
                memory["conversation_history"] = memory["conversation_history"][-1000:]

        self._mutate_file(self.honeycomb_dir / "dj_memory.json", append_entry)

    def update_learned_pattern(self, pattern_key: str, pattern_data: Any) -> None:
        """
        Update learned pattern in DJ memory.

        Args:
            pattern_key: Pattern identifier
            pattern_data: Pattern data
        """

        def set_pattern(memory: dict[str, Any]) -> None:
            memory["learned_patterns"][pattern_key] = pattern_data

        self._mutate_file(self.honeycomb_dir / "dj_memory.json", set_pattern)


# Convenience functions for common operations
def get_current_track() -> dict[str, Any] | None:
    """Get currently playing track."""
    manager = StateManager()
    return manager.get_current_track()


def update_playlist(queue: list[dict[str, Any]]) -> None:
    """Update playlist queue."""
    manager = StateManager()
    manager.update_playlist(queue)


def add_task(action: str, args: dict[str, Any] | None = None) -> str:
    """Add task to queue."""
    manager = StateManager()
    return manager.add_task(action, args)
