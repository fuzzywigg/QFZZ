"""MusicPlayer.seek inclusive duration boundary (position == duration allowed)."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer


def test_seek_at_duration_ok_beyond_rejected(tmp_path: Path):
    (tmp_path / "a.wav").write_bytes(b"RIFF")
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "a.wav", "duration": 10}]
        )
        assert player.play(0) is True
        assert player.seek(10) is True
        assert player.get_position() == 10
        assert player.seek(11) is False
        assert player.get_position() == 10
    finally:
        player.stop()
        player.server.stop()
