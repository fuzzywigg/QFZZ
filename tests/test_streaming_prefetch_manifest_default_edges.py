"""Empty-playlist prefetch clear and default HLS manifest when provider unset."""

import urllib.request
from pathlib import Path

from qfzz.streaming.player import MusicPlayer
from qfzz.streaming.server import AudioRequestHandler, StreamingServer


def test_compute_prefetch_clears_when_playlist_empty(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, prefetch_count=2)
    try:
        player._playlist = []
        player._current_index = -1
        player._prefetch_queue = [{"title": "stale"}]
        player._compute_prefetch_queue()
        assert player._prefetch_queue == []
    finally:
        player.server.stop()


def test_manifest_default_when_provider_not_callable(tmp_path: Path):
    AudioRequestHandler.STREAM_MANIFEST_PROVIDER = None
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    try:
        url = f"http://localhost:{server.port}/stream/manifest.m3u8"
        with urllib.request.urlopen(url) as response:
            body = response.read().decode("utf-8")
        assert body.startswith("#EXTM3U")
        assert "#EXT-X-ENDLIST" in body
    finally:
        server.stop()
        AudioRequestHandler.STREAM_MANIFEST_PROVIDER = None
