"""
Icecast Source Client for QFZZ.
Streams audio to Icecast server using libshout/shout-python.
"""

import logging
import os
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Optional shout dependency - graceful fallback
try:
    import shout
    SHOUT_AVAILABLE = True
except ImportError:
    SHOUT_AVAILABLE = False
    logger.warning("shout-python not available. Icecast streaming disabled.")


class IcecastState(Enum):
    """Icecast client state."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"


@dataclass
class IcecastConfig:
    """Icecast server configuration."""
    host: str = "localhost"
    port: int = 8000
    password: str = "hackme"
    mount: str = "/qfzz"

    # Stream metadata
    name: str = "QFZZ - The Pulse of the Quantum Realm"
    description: str = "AI-powered personalized radio"
    genre: str = "Electronic/Ambient"
    url: str = "https://github.com/fuzzywigg/QFZZ"

    # Audio format
    format: str = "mp3"  # or "ogg"
    bitrate: int = 128  # kbps
    samplerate: int = 44100  # Hz
    channels: int = 2  # stereo

    # Connection settings
    protocol: str = "http"  # or "https"
    reconnect_attempts: int = 3
    reconnect_delay: float = 5.0  # seconds

    # Public stream?
    public: bool = False


class IcecastClient:
    """
    Icecast source client for streaming audio.

    This client connects to an Icecast server and streams audio data.
    It handles reconnection, metadata updates, and error recovery.
    """

    def __init__(self, config: IcecastConfig | None = None):
        """
        Initialize Icecast client.

        Args:
            config: Icecast configuration (uses defaults if None)
        """
        self.config = config or IcecastConfig()
        self._state = IcecastState.DISCONNECTED
        self._shout: Any | None = None
        self._streaming_thread: threading.Thread | None = None
        self._stop_flag = threading.Event()
        self._current_track: dict[str, Any] | None = None
        self._bytes_sent = 0
        self._connection_time: float | None = None

        if not SHOUT_AVAILABLE:
            logger.error("Cannot initialize Icecast client: shout-python not installed")
            logger.info("Install with: pip install shout-python")
            self._state = IcecastState.ERROR

    def connect(self) -> bool:
        """
        Connect to Icecast server.

        Returns:
            True if connected successfully, False otherwise
        """
        if not SHOUT_AVAILABLE:
            logger.error("Cannot connect: shout-python not available")
            return False

        try:
            # Create shout object
            self._shout = shout.Shout()

            # Configure connection
            self._shout.host = self.config.host
            self._shout.port = self.config.port
            self._shout.password = self.config.password
            self._shout.mount = self.config.mount
            self._shout.protocol = self.config.protocol

            # Configure stream metadata
            self._shout.name = self.config.name
            self._shout.description = self.config.description
            self._shout.genre = self.config.genre
            self._shout.url = self.config.url
            self._shout.public = 1 if self.config.public else 0

            # Configure audio format
            if self.config.format == "mp3":
                self._shout.format = "mp3"
                self._shout.audio_info = {
                    shout.SHOUT_AI_BITRATE: str(self.config.bitrate),
                    shout.SHOUT_AI_SAMPLERATE: str(self.config.samplerate),
                    shout.SHOUT_AI_CHANNELS: str(self.config.channels),
                }
            elif self.config.format == "ogg":
                self._shout.format = "ogg"
                self._shout.audio_info = {
                    shout.SHOUT_AI_BITRATE: str(self.config.bitrate),
                    shout.SHOUT_AI_SAMPLERATE: str(self.config.samplerate),
                    shout.SHOUT_AI_CHANNELS: str(self.config.channels),
                }

            # Attempt connection
            self._shout.open()
            self._state = IcecastState.CONNECTED
            self._connection_time = time.time()
            self._bytes_sent = 0

            logger.info(
                f"Connected to Icecast server at {self.config.host}:{self.config.port}{self.config.mount}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Icecast: {e}")
            self._state = IcecastState.ERROR
            return False

    def disconnect(self) -> None:
        """Disconnect from Icecast server."""
        if self._shout:
            try:
                self._shout.close()
                logger.info("Disconnected from Icecast server")
            except Exception as e:
                logger.error(f"Error disconnecting from Icecast: {e}")
            finally:
                self._shout = None
                self._state = IcecastState.DISCONNECTED
                self._connection_time = None

    def update_metadata(self, track: dict[str, Any]) -> bool:
        """
        Update stream metadata (now playing info).

        Args:
            track: Track dictionary with title, artist, etc.

        Returns:
            True if successful, False otherwise
        """
        if not self._shout or self._state == IcecastState.DISCONNECTED:
            logger.warning("Cannot update metadata: not connected")
            return False

        try:
            # Format metadata string
            title = track.get("title", "Unknown Title")
            artist = track.get("artist", "Unknown Artist")
            metadata_str = f"{artist} - {title}"

            # Update Icecast metadata
            metadata = shout.Metadata()
            metadata.add("song", metadata_str)
            self._shout.set_metadata(metadata)

            self._current_track = track
            logger.info(f"Updated metadata: {metadata_str}")
            return True

        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False

    def send_audio(self, audio_data: bytes) -> bool:
        """
        Send audio data to Icecast server.

        Args:
            audio_data: Raw audio bytes

        Returns:
            True if sent successfully, False otherwise
        """
        if not self._shout or self._state == IcecastState.DISCONNECTED:
            logger.warning("Cannot send audio: not connected")
            return False

        try:
            # Send data to Icecast
            self._shout.send(audio_data)
            self._shout.sync()

            self._bytes_sent += len(audio_data)
            self._state = IcecastState.STREAMING
            return True

        except Exception as e:
            logger.error(f"Failed to send audio data: {e}")
            self._state = IcecastState.ERROR
            return False

    def stream_file(self, filepath: str, chunk_size: int = 4096) -> bool:
        """
        Stream an audio file to Icecast.

        Args:
            filepath: Path to audio file
            chunk_size: Size of chunks to read/send

        Returns:
            True if streamed successfully, False otherwise
        """
        if not os.path.exists(filepath):
            logger.error(f"Audio file not found: {filepath}")
            return False

        if not self._shout or self._state == IcecastState.DISCONNECTED:
            logger.warning("Cannot stream file: not connected")
            return False

        try:
            with open(filepath, "rb") as f:
                while not self._stop_flag.is_set():
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break  # EOF

                    if not self.send_audio(chunk):
                        return False

            logger.info(f"Finished streaming: {os.path.basename(filepath)}")
            return True

        except Exception as e:
            logger.error(f"Error streaming file: {e}")
            return False

    def start_streaming_thread(self, playlist_callback) -> bool:
        """
        Start streaming in background thread.

        Args:
            playlist_callback: Function that returns next track filepath

        Returns:
            True if started successfully
        """
        if self._streaming_thread and self._streaming_thread.is_alive():
            logger.warning("Streaming thread already running")
            return False

        self._stop_flag.clear()
        self._streaming_thread = threading.Thread(
            target=self._streaming_loop,
            args=(playlist_callback,),
            daemon=True
        )
        self._streaming_thread.start()
        logger.info("Started streaming thread")
        return True

    def stop_streaming_thread(self) -> None:
        """Stop streaming thread."""
        self._stop_flag.set()
        if self._streaming_thread:
            self._streaming_thread.join(timeout=5.0)
            logger.info("Stopped streaming thread")

    def _streaming_loop(self, playlist_callback) -> None:
        """
        Main streaming loop (runs in background thread).

        Args:
            playlist_callback: Function that returns next track filepath
        """
        logger.info("Streaming loop started")

        while not self._stop_flag.is_set():
            try:
                # Get next track
                track = playlist_callback()
                if not track:
                    logger.warning("No track available, waiting...")
                    time.sleep(1.0)
                    continue

                # Update metadata
                self.update_metadata(track)

                # Stream the file
                filepath = track.get("filepath")
                if filepath and os.path.exists(filepath):
                    self.stream_file(filepath)
                else:
                    logger.error(f"Track file not found: {filepath}")
                    time.sleep(1.0)

            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")
                time.sleep(5.0)  # Brief pause before retry

        logger.info("Streaming loop ended")

    def get_state(self) -> IcecastState:
        """Get current client state."""
        return self._state

    def get_stats(self) -> dict[str, Any]:
        """
        Get streaming statistics.

        Returns:
            Dictionary of stats
        """
        uptime = None
        if self._connection_time:
            uptime = time.time() - self._connection_time

        return {
            "state": self._state.value,
            "connected": self._state in [IcecastState.CONNECTED, IcecastState.STREAMING],
            "bytes_sent": self._bytes_sent,
            "uptime_seconds": uptime,
            "current_track": self._current_track,
            "server": f"{self.config.host}:{self.config.port}{self.config.mount}",
        }

    def __del__(self):
        """Cleanup on deletion."""
        self.stop_streaming_thread()
        self.disconnect()
