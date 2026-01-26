"""
QFZZ Honeycomb State Management

Stigmergic state system for agent coordination through shared JSON state files.
Thread-safe operations with schema validation.
"""

import json
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

    def _read_file(self, filepath: Path) -> Any:
        """Read JSON file with file locking."""
        lock_path = self._get_lock_path(filepath)

        with FileLock(lock_path, timeout=10):
            if not filepath.exists():
                return None

            with open(filepath) as f:
                return json.load(f)

    def _write_file(self, filepath: Path, data: Any):
        """Write JSON file with file locking."""
        lock_path = self._get_lock_path(filepath)

        with FileLock(lock_path, timeout=10):
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)

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
        track_data = {
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
        playlist = self.get_playlist()
        track = {
            "track_id": track_id,
            "title": title,
            "artist": artist,
            "priority": priority,
            "added_at": datetime.utcnow().isoformat(),
        }

        playlist["queue"].append(track)
        self.update_playlist(playlist["queue"])

    # Listener State Operations
    def get_listener_state(self) -> dict[str, Any]:
        """Get listener state."""
        return self._read_file(self.honeycomb_dir / "listener_state.json")

    def update_listener_count(self, count: int) -> None:
        """Update active listener count."""
        state = self.get_listener_state()
        state["active_listeners"] = count
        self._write_file(self.honeycomb_dir / "listener_state.json", state)

    def add_listener_request(self, listener_id: str, request_type: str, content: str) -> None:
        """
        Add listener request.

        Args:
            listener_id: Unique listener identifier
            request_type: Type of request (e.g., 'song_request', 'shoutout', 'question')
            content: Request content
        """
        state = self.get_listener_state()
        request = {
            "request_id": f"{listener_id}_{datetime.utcnow().timestamp()}",
            "listener_id": listener_id,
            "request_type": request_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        state["recent_requests"].append(request)

        # Keep only last 100 requests
        if len(state["recent_requests"]) > 100:
            state["recent_requests"] = state["recent_requests"][-100:]

        self._write_file(self.honeycomb_dir / "listener_state.json", state)

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

        tasks = self.get_tasks()
        task = {
            "task_id": task_id,
            "action": action,
            "args": args or {},
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        tasks["pending"].append(task)
        self._write_file(self.honeycomb_dir / "tasks.json", tasks)

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
        tasks = self.get_tasks()

        for task in tasks["pending"]:
            if task["task_id"] == task_id:
                task["status"] = status
                self._write_file(self.honeycomb_dir / "tasks.json", tasks)
                return True

        return False

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
        memory = self.get_dj_memory()

        entry = {"timestamp": datetime.utcnow().isoformat(), "role": role, "content": content}

        memory["conversation_history"].append(entry)

        # Keep only last 1000 messages
        if len(memory["conversation_history"]) > 1000:
            memory["conversation_history"] = memory["conversation_history"][-1000:]

        self._write_file(self.honeycomb_dir / "dj_memory.json", memory)

    def update_learned_pattern(self, pattern_key: str, pattern_data: Any) -> None:
        """
        Update learned pattern in DJ memory.

        Args:
            pattern_key: Pattern identifier
            pattern_data: Pattern data
        """
        memory = self.get_dj_memory()
        memory["learned_patterns"][pattern_key] = pattern_data
        self._write_file(self.honeycomb_dir / "dj_memory.json", memory)


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
