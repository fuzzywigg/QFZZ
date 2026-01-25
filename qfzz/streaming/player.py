"""
Music player for streaming playback.
"""

from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime
from enum import Enum

from .server import StreamingServer
from .audio_tools import generate_tone

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
    
    def __init__(self, content_dir: str = "./audio_content", port: int = 8000):
        """
        Initialize music player.
        
        Args:
            content_dir: Directory to serve audio from
            port: Streaming port
        """
        self._state = PlayerState.STOPPED
        self._current_track: Optional[Dict[str, Any]] = None
        self._playlist: List[Dict[str, Any]] = []
        self._current_index = -1
        self._volume = 0.8
        self._position_seconds = 0
        self._playback_history: List[Dict[str, Any]] = []
        
        # Setup content directory
        self.content_dir = os.path.abspath(content_dir)
        os.makedirs(self.content_dir, exist_ok=True)
        
        # Initialize streaming server
        self.server = StreamingServer(self.content_dir, port)
        self.server.start()
        
        # Ensure we have at least one test track
        self._ensure_test_content()
        
        logger.info(f"Music Player initialized. Streaming at http://localhost:{port}")
    
    def _ensure_test_content(self):
        """Generate test audio files if they don't exist."""
        test_file = os.path.join(self.content_dir, "test_tone.wav")
        if not os.path.exists(test_file):
            generate_tone(test_file, duration_sec=5, freq_hz=440)
            generate_tone(os.path.join(self.content_dir, "intro.wav"), duration_sec=3, freq_hz=554) # C#5
            logger.info("Generated test audio content")

    def get_stream_url(self, filename: str) -> str:
        """Get the streaming URL for a file."""
        return f"http://localhost:{self.server.port}/{filename}"
        
    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'server'):
            self.server.stop()

        """
        Load a playlist.
        
        Args:
            tracks: List of track dictionaries
        """
        self._playlist = tracks.copy()
        self._current_index = -1
        logger.info(f"Loaded playlist with {len(tracks)} tracks")
    
    def play(self, track_index: Optional[int] = None) -> bool:
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
        self._state = PlayerState.PLAYING
        self._position_seconds = 0
        
        # Record playback start
        self._record_playback_event('play_start')
        
        logger.info(f"Playing: {self._current_track.get('title', 'Unknown')} by {self._current_track.get('artist', 'Unknown')}")
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
        self._record_playback_event('pause')
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
        self._record_playback_event('resume')
        logger.info("Playback resumed")
        return True
    
    def stop(self) -> None:
        """Stop playback."""
        if self._current_track:
            self._record_playback_event('stop')
        
        self._state = PlayerState.STOPPED
        self._current_track = None
        self._position_seconds = 0
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
            self._record_playback_event('skip')
        
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
        
        duration = self._current_track.get('duration', 0)
        if position_seconds < 0 or position_seconds > duration:
            logger.error(f"Invalid seek position: {position_seconds}")
            return False
        
        self._position_seconds = position_seconds
        self._record_playback_event('seek', {'position': position_seconds})
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
    
    def get_current_track(self) -> Optional[Dict[str, Any]]:
        """Get currently playing track."""
        return self._current_track
    
    def get_position(self) -> int:
        """Get current playback position in seconds."""
        return self._position_seconds
    
    def get_volume(self) -> float:
        """Get current volume level."""
        return self._volume
    
    def get_playlist(self) -> List[Dict[str, Any]]:
        """Get current playlist."""
        return self._playlist.copy()
    
    def get_playlist_info(self) -> Dict[str, Any]:
        """
        Get playlist information.
        
        Returns:
            Dictionary of playlist info
        """
        return {
            'track_count': len(self._playlist),
            'current_index': self._current_index,
            'current_track': self._current_track,
            'total_duration': sum(t.get('duration', 0) for t in self._playlist)
        }
    
    def get_playback_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get playback history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of playback events
        """
        return self._playback_history[-limit:]
    
    def _record_playback_event(self, event_type: str, 
                               metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a playback event.
        
        Args:
            event_type: Type of event
            metadata: Optional event metadata
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'track': self._current_track,
            'position': self._position_seconds,
            'metadata': metadata or {}
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
