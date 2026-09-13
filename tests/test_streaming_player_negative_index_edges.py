"""MusicPlayer.play rejects negative track indexes."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer, PlayerState


def test_play_negative_index_stays_stopped(tmp_path: Path):
    (tmp_path / "a.wav").write_bytes(b"RIFF")
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "a.wav", "duration": 5}]
        )
        assert player.play(-1) is False
        assert player.get_state() == PlayerState.STOPPED
        assert player.get_current_track() is None
    finally:
        player.server.stop()
