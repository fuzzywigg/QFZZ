"""MusicPlayer.report_stream_error with no current track cannot reconnect."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer, PlayerState


def test_recoverable_error_without_current_track_stays_stopped(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, reconnect_max_attempts=3)
    try:
        player._playlist = []
        player._current_track = None
        assert player.report_stream_error("ghost reconnect", recoverable=True) is False
        assert player.get_state() == PlayerState.STOPPED
    finally:
        player.server.stop()
