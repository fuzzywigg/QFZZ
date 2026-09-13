"""HLS EXTINF falls back to Unknown artist/title when metadata keys missing."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer


def test_hls_manifest_unknown_artist_title_defaults(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        # Bypass file validation to hit get_hls_manifest .get defaults directly.
        player._playlist = [{"filename": "bare.wav", "duration": 5}]
        manifest = player.get_hls_manifest()
        assert "#EXTINF:5,Unknown - Unknown" in manifest
        assert "/bare.wav" in manifest
    finally:
        player.server.stop()
