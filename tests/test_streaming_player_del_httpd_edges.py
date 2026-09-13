"""MusicPlayer __del__ and add_track when httpd is None."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from qfzz.streaming.player import MusicPlayer


def test_del_invokes_server_stop(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    stop = MagicMock()
    player.server.stop = stop
    player.__del__()
    stop.assert_called_once()


def test_add_track_when_httpd_none_uses_empty_payload_branch(tmp_path: Path):
    with patch("qfzz.streaming.player.StreamingServer") as server_cls:
        server = MagicMock()
        server.start.return_value = False
        server.httpd = None
        server_cls.return_value = server
        player = MusicPlayer(content_dir=str(tmp_path), port=0)
        # Avoid auto content noise; inject validated track path via file
        wav = tmp_path / "clip.wav"
        wav.write_bytes(b"RIFF....WAVE")
        player.content_dir = str(tmp_path)
        player.add_track(
            {
                "title": "Clip",
                "artist": "A",
                "filename": "clip.wav",
                "duration": 3,
            }
        )
        server.set_playlist.assert_called()
        # Last set_playlist call should include appended track
        args = server.set_playlist.call_args[0][0]
        assert isinstance(args, list)
        assert any(t.get("title") == "Clip" for t in args)
