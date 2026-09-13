"""MusicPlayer HLS zero-duration floor and negative seek edges."""

from qfzz.audio.generator import generate_tone
from qfzz.streaming.player import MusicPlayer


def test_hls_manifest_floors_zero_and_missing_duration(tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    generate_tone(str(a), duration_sec=1, freq_hz=440)
    generate_tone(str(b), duration_sec=1, freq_hz=554)

    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [
                {"title": "Zero", "artist": "A", "filename": "a.wav", "duration": 0},
                {"title": "Missing", "artist": "B", "filename": "b.wav"},
            ]
        )
        manifest = player.get_hls_manifest()
        assert "#EXTINF:1,A - Zero" in manifest
        assert "#EXTINF:1,B - Missing" in manifest
        assert "/a.wav" in manifest
        assert "/b.wav" in manifest
        assert manifest.strip().endswith("#EXT-X-ENDLIST")
    finally:
        player.server.stop()


def test_seek_negative_rejected(tmp_path):
    wav = tmp_path / "c.wav"
    generate_tone(str(wav), duration_sec=1, freq_hz=220)
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "C", "filename": "c.wav", "duration": 10}]
        )
        assert player.play(0) is True
        assert player.seek(-1) is False
        assert player.get_position() == 0
    finally:
        player.server.stop()
