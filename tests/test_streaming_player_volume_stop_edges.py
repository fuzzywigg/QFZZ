"""MusicPlayer set_volume lower bound and stop without current track."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer, PlayerState


def test_set_volume_rejects_below_zero_and_accepts_zero(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        assert player.set_volume(-0.1) is False
        assert player.set_volume(0.0) is True
        assert player._volume == 0.0
    finally:
        player.server.stop()


def test_stop_without_current_track_records_no_stop_event(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player._current_track = None
        before = list(player._playback_history)
        player.stop()
        assert player.get_state() == PlayerState.STOPPED
        assert player._playback_history == before
        assert not any(e.get("event") == "stop" for e in player._playback_history)
    finally:
        player.server.stop()
