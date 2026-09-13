"""StreamingServer default HLS manifest and MusicPlayer seek missing duration."""

import urllib.request
from pathlib import Path

from qfzz.streaming.player import MusicPlayer
from qfzz.streaming.server import StreamingServer


def test_default_manifest_when_no_provider(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    # Explicitly clear any provider
    server.set_stream_manifest_provider(None)
    from qfzz.streaming.server import AudioRequestHandler

    AudioRequestHandler.STREAM_MANIFEST_PROVIDER = None
    base = f"http://localhost:{server.port}"
    try:
        with urllib.request.urlopen(f"{base}/stream/manifest.m3u8") as response:
            body = response.read().decode()
        assert body.startswith("#EXTM3U")
        assert "#EXT-X-ENDLIST" in body
    finally:
        server.stop()


def test_seek_missing_duration_key_rejects_positive_position(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "intro.wav", "duration": 10}]
        )
        assert player.play(0) is True
        # Simulate track without duration key (get defaults to 0)
        player._current_track = {
            k: v for k, v in player._current_track.items() if k != "duration"
        }
        assert "duration" not in player._current_track
        assert player.seek(1) is False
        assert player.seek(0) is True
    finally:
        player.server.stop()
