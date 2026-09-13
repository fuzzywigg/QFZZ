"""MusicPlayer.set_volume inclusive upper bound edges."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer


def test_volume_accepts_one_rejects_above(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        assert player.set_volume(1.0) is True
        assert player.get_volume() == 1.0
        assert player.set_volume(1.01) is False
        assert player.get_volume() == 1.0
    finally:
        player.server.stop()
