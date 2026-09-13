"""MusicPlayer.seek rejects negative position; add_track appends validated file."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer


def test_seek_negative_rejected_and_add_track_appends(tmp_path: Path):
    (tmp_path / "a.wav").write_bytes(b"RIFF")
    (tmp_path / "b.wav").write_bytes(b"RIFF")
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "a.wav", "duration": 8}]
        )
        assert player.play(0) is True
        assert player.seek(-1) is False
        assert player.get_position() == 0

        player.add_track(
            {"title": "B", "artist": "Y", "filename": "b.wav", "duration": 6}
        )
        titles = [t["title"] for t in player.get_playlist()]
        assert titles == ["A", "B"]
    finally:
        player.stop()
        player.server.stop()
