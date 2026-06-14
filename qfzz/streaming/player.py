"""
Music player for streaming playback.
"""

import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any

from qfzz.datasets.manager import DatasetManager

from .audio_tools import generate_tone
from .server import StreamingServer

logger = logging.getLogger(__name__)


class PlayerState(Enum):
    """Player state enumeration."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    BUFFERING = "buffering"


class MusicPlayer:
    """
    Music player for streaming playback.

    Manages a local streaming server and playlist state.
    """

    def __init__(
        self,
        content_dir: str = "./audio_content",
        port: int = 8000,
        dataset_manager: DatasetManager | None = None,
        buffer_seconds: int = 8,
        prefetch_count: int = 2,
        reconnect_max_attempts: int = 3,
    ):
        """
        Initialize music player.

        Args:
            content_dir: Directory to serve audio from
            port: Streaming port
        """
        self._state = PlayerState.STOPPED
        self._current_track: dict[str, Any] | None = None
        self._playlist: list[dict[str, Any]] = []
        self._current_index = -1
        self._volume = 0.8
        self._position_seconds = 0
        self._playback_history: list[dict[str, Any]] = []
        self._prefetch_queue: list[dict[str, Any]] = []
        self._reconnect_attempts = 0
        self._reconnect_max_attempts = max(1, reconnect_max_attempts)
        self._last_error: str | None = None
        self._buffer_seconds = max(2, buffer_seconds)
        self._prefetch_count = max(1, prefetch_count)
        self._dataset_manager = dataset_manager

        # Setup content directory
        self.content_dir = os.path.abspath(content_dir)
        os.makedirs(self.content_dir, exist_ok=True)

        # Initialize streaming server
        self.server = StreamingServer(self.content_dir, port)
        self.server.start()
        self.server.set_stream_status_provider(self.get_stream_status)
        self.server.set_stream_manifest_provider(self.get_hls_manifest)
        self.server.set_stream_error_handler(self.report_stream_error)

        # Ensure we have at least one test track
        self._ensure_test_content()
        self._sync_stream_status()

        logger.info(f"Music Player initialized. Streaming at http://localhost:{port}")

    def _ensure_test_content(self):
        """Generate test audio files if they don't exist."""
        test_file = os.path.join(self.content_dir, "test_tone.wav")
        if not os.path.exists(test_file):
            generate_tone(test_file, duration_sec=5, freq_hz=440)
            generate_tone(
                os.path.join(self.content_dir, "intro.wav"), duration_sec=3, freq_hz=554
            )  # C#5
            logger.info("Generated test audio content")

    def get_stream_url(self, filename: str) -> str:
        """Get the streaming URL for a file."""
        return f"http://localhost:{self.server.port}/{filename}"

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, "server"):
            self.server.stop()

    def load_playlist(self, tracks: list[dict[str, Any]]) -> None:
        """
        Load a playlist.

        Args:
            tracks: List of track dictionaries
        """
        validated_tracks = self._validate_tracks(tracks)
        self._playlist = validated_tracks
        self._current_index = -1
        self._current_track = None
        self._prefetch_queue = []
        self._reconnect_attempts = 0
        self._last_error = None

        # Update server payload for dynamic API
        # Enrich tracks with full URLs
        api_playlist = []
        for track in self._playlist:
            t = track.copy()
            t["url"] = self.get_stream_url(track["filename"])
            api_playlist.append(t)

        self.server.set_playlist(api_playlist)
        self._sync_stream_status()

        logger.info(f"Loaded playlist with {len(self._playlist)} tracks")

    def add_track(self, track: dict[str, Any]) -> None:
        """Add a single track to the playlist."""
        validated = self._validate_tracks([track])
        if not validated:
            logger.warning("Rejected non-streamable track")
            return

        track = validated[0]
        self._playlist.append(track)

        # Update Server
        t = track.copy()
        t["url"] = self.get_stream_url(track["filename"])

        # Retrieve current payload and append to avoid full reload issues
        current = self.server.httpd.RequestHandlerClass.PAYLOAD if self.server.httpd else []
        current.append(t)
        self.server.set_playlist(current)
        self._sync_stream_status()

        logger.info(f"Added track to playlist: {track['title']}")

    def set_dj_message(self, message: str):
        """Update DJ message on server."""
        self.server.set_dj_message(message)

    def set_ledger_stats(self, stats: dict):
        """Update ledger stats on server."""
        self.server.set_ledger_stats(stats)

    def play(self, track_index: int | None = None) -> bool:
        """
        Start playback.

        Args:
            track_index: Optional track index to play (default: next track)

        Returns:
            True if playback started, False otherwise
        """
        if not self._playlist:
            logger.warning("Cannot play: playlist is empty")
            return False

        if track_index is not None:
            if not 0 <= track_index < len(self._playlist):
                logger.error(f"Invalid track index: {track_index}")
                return False
            self._current_index = track_index
        else:
            # Play next track
            self._current_index = (self._current_index + 1) % len(self._playlist)

        self._current_track = self._playlist[self._current_index]
        self._state = PlayerState.BUFFERING
        self._position_seconds = 0
        self._reconnect_attempts = 0
        self._last_error = None
        self._compute_prefetch_queue()
        self._state = PlayerState.PLAYING

        # Record playback start
        self._record_playback_event("play_start")
        self._sync_stream_status()

        logger.info(
            f"Playing: {self._current_track.get('title', 'Unknown')} by {self._current_track.get('artist', 'Unknown')}"
        )
        return True

    def pause(self) -> bool:
        """
        Pause playback.

        Returns:
            True if paused, False if not playing
        """
        if self._state != PlayerState.PLAYING:
            logger.warning("Cannot pause: not currently playing")
            return False

        self._state = PlayerState.PAUSED
        self._record_playback_event("pause")
        self._sync_stream_status()
        logger.info("Playback paused")
        return True

    def resume(self) -> bool:
        """
        Resume playback.

        Returns:
            True if resumed, False if not paused
        """
        if self._state != PlayerState.PAUSED:
            logger.warning("Cannot resume: not currently paused")
            return False

        self._state = PlayerState.PLAYING
        self._record_playback_event("resume")
        self._sync_stream_status()
        logger.info("Playback resumed")
        return True

    def stop(self) -> None:
        """Stop playback."""
        if self._current_track:
            self._record_playback_event("stop")

        self._state = PlayerState.STOPPED
        self._current_track = None
        self._position_seconds = 0
        self._prefetch_queue = []
        self._sync_stream_status()
        logger.info("Playback stopped")

    def next_track(self) -> bool:
        """
        Skip to next track.

        Returns:
            True if skipped, False if at end of playlist
        """
        if not self._playlist:
            return False

        if self._current_track:
            self._record_playback_event("skip")

        next_index = (self._current_index + 1) % len(self._playlist)
        return self.play(next_index)

    def previous_track(self) -> bool:
        """
        Go to previous track.

        Returns:
            True if successful, False otherwise
        """
        if not self._playlist:
            return False

        prev_index = (self._current_index - 1) % len(self._playlist)
        return self.play(prev_index)

    def seek(self, position_seconds: int) -> bool:
        """
        Seek to position in current track.

        Args:
            position_seconds: Position in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self._current_track:
            logger.warning("Cannot seek: no track playing")
            return False

        duration = self._current_track.get("duration", 0)
        if position_seconds < 0 or position_seconds > duration:
            logger.error(f"Invalid seek position: {position_seconds}")
            return False

        self._position_seconds = position_seconds
        self._record_playback_event("seek", {"position": position_seconds})
        self._sync_stream_status()
        logger.debug(f"Seeked to {position_seconds}s")
        return True

    def set_volume(self, volume: float) -> bool:
        """
        Set playback volume.

        Args:
            volume: Volume level (0.0-1.0)

        Returns:
            True if successful, False otherwise
        """
        if not 0.0 <= volume <= 1.0:
            logger.error(f"Invalid volume: {volume}")
            return False

        self._volume = volume
        logger.debug(f"Volume set to {volume:.1%}")
        return True

    def get_state(self) -> PlayerState:
        """Get current player state."""
        return self._state

    def get_current_track(self) -> dict[str, Any] | None:
        """Get currently playing track."""
        return self._current_track

    def get_position(self) -> int:
        """Get current playback position in seconds."""
        return self._position_seconds

    def get_volume(self) -> float:
        """Get current volume level."""
        return self._volume

    def get_playlist(self) -> list[dict[str, Any]]:
        """Get current playlist."""
        return self._playlist.copy()

    def get_stream_status(self) -> dict[str, Any]:
        """Get stream session status for clients."""
        return {
            "state": self._state.value,
            "current_track": (
                {
                    **self._current_track,
                    "url": self.get_stream_url(self._current_track["filename"]),
                }
                if self._current_track
                else None
            ),
            "prefetch_tracks": [
                {**track, "url": self.get_stream_url(track["filename"])}
                for track in self._prefetch_queue
            ],
            "buffer_seconds": self._buffer_seconds,
            "reconnect": {
                "attempts": self._reconnect_attempts,
                "max_attempts": self._reconnect_max_attempts,
            },
            "error": self._last_error,
        }

    def get_hls_manifest(self) -> str:
        """Build a simple HLS manifest from the active playlist."""
        if not self._playlist:
            return "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-ENDLIST\n"

        lines = [
            "#EXTM3U",
            "#EXT-X-VERSION:3",
            "#EXT-X-TARGETDURATION:10",
            "#EXT-X-MEDIA-SEQUENCE:0",
        ]
        for track in self._playlist:
            duration = max(1, int(track.get("duration", 0) or 1))
            lines.append(f"#EXTINF:{duration},{track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')}")
            lines.append(f"/{track['filename']}")
        lines.append("#EXT-X-ENDLIST")
        return "\n".join(lines) + "\n"

    def report_stream_error(self, error_message: str, recoverable: bool = True) -> bool:
        """
        Handle playback error and attempt reconnect when possible.

        Returns:
            True if recovered, False if stream should remain failed/stopped.
        """
        self._last_error = error_message
        self._record_playback_event("stream_error", {"error": error_message})
        if recoverable and self._current_track and self._reconnect_attempts < self._reconnect_max_attempts:
            self._reconnect_attempts += 1
            self._state = PlayerState.BUFFERING
            self._record_playback_event(
                "reconnect_attempt",
                {"attempt": self._reconnect_attempts, "error": error_message},
            )
            self._compute_prefetch_queue()
            self._state = PlayerState.PLAYING
            self._sync_stream_status()
            logger.warning(
                "Recovered from stream error on attempt %s/%s: %s",
                self._reconnect_attempts,
                self._reconnect_max_attempts,
                error_message,
            )
            return True

        self._state = PlayerState.STOPPED
        self._sync_stream_status()
        logger.error("Stream failed permanently: %s", error_message)
        return False

    def load_playlist_from_datasets(
        self, dataset_ids: list[str] | None = None, min_quality: float = 0.0
    ) -> int:
        """Load streamable tracks discovered via DatasetManager."""
        if not self._dataset_manager:
            logger.warning("Dataset manager not configured for player")
            return 0
        tracks = self._dataset_manager.build_streamable_playlist(
            content_dir=self.content_dir,
            dataset_ids=dataset_ids,
            min_quality=min_quality,
        )
        self.load_playlist(tracks)
        return len(tracks)

    def get_playlist_info(self) -> dict[str, Any]:
        """
        Get playlist information.

        Returns:
            Dictionary of playlist info
        """
        return {
            "track_count": len(self._playlist),
            "current_index": self._current_index,
            "current_track": self._current_track,
            "total_duration": sum(t.get("duration", 0) for t in self._playlist),
        }

    def get_playback_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get playback history.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of playback events
        """
        return self._playback_history[-limit:]

    def _record_playback_event(
        self, event_type: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Record a playback event.

        Args:
            event_type: Type of event
            metadata: Optional event metadata
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "track": self._current_track,
            "position": self._position_seconds,
            "metadata": metadata or {},
        }

        self._playback_history.append(event)

        # Keep only last 100 events
        if len(self._playback_history) > 100:
            self._playback_history = self._playback_history[-100:]

    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._state == PlayerState.PLAYING

    def is_paused(self) -> bool:
        """Check if currently paused."""
        return self._state == PlayerState.PAUSED

    def is_stopped(self) -> bool:
        """Check if stopped."""
        return self._state == PlayerState.STOPPED

    def _validate_tracks(self, tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize and validate track entries for local streaming."""
        validated: list[dict[str, Any]] = []
        for track in tracks:
            filename = track.get("filename")
            filepath = track.get("filepath")
            resolved_path = ""

            if filepath:
                resolved_path = (
                    filepath
                    if os.path.isabs(filepath)
                    else os.path.join(self.content_dir, filepath)
                )
            elif filename:
                resolved_path = os.path.join(self.content_dir, filename)
            else:
                continue

            if not os.path.isfile(resolved_path):
                logger.warning("Skipping track with missing file: %s", resolved_path)
                continue

            normalized = track.copy()
            normalized["filename"] = os.path.basename(resolved_path)
            normalized["filepath"] = resolved_path
            normalized.setdefault("title", normalized["filename"])
            normalized.setdefault("artist", "Unknown Artist")
            normalized.setdefault("genre", "Unknown")
            normalized.setdefault("duration", int(normalized.get("duration", 0) or 0))
            validated.append(normalized)
        return validated

    def _compute_prefetch_queue(self) -> None:
        """Compute upcoming tracks to prefetch on clients."""
        if not self._playlist or self._current_index < 0:
            self._prefetch_queue = []
            return
        queue: list[dict[str, Any]] = []
        for offset in range(1, self._prefetch_count + 1):
            idx = (self._current_index + offset) % len(self._playlist)
            queue.append(self._playlist[idx])
        self._prefetch_queue = queue

    def _sync_stream_status(self) -> None:
        """Push latest stream status to HTTP API payload."""
        self.server.set_stream_status(self.get_stream_status())
