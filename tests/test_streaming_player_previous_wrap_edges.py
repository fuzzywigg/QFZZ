"""MusicPlayer.previous_track wraps from index 0 to last track."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer


def test_previous_from_first_wraps_to_last(tmp_path: Path):
    (tmp_path / "a.wav").write_bytes(b"RIFF")
    (tmp_path / "b.wav").write_bytes(b"RIFF")
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [
                {"title": "First", "artist": "X", "filename": "a.wav", "duration": 5},
                {"title": "Last", "artist": "Y", "filename": "b.wav", "duration": 5},
            ]
        )
        assert player.play(0) is True
        assert player.get_current_track()["title"] == "First"
        assert player.previous_track() is True
        assert player.get_current_track()["title"] == "Last"
    finally:
        player.stop()
        player.server.stop()
