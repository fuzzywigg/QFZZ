"""MusicPlayer._validate_tracks setdefault title/artist/genre from filepath-only."""

from qfzz.audio.generator import generate_tone
from qfzz.streaming.player import MusicPlayer


def test_validate_filepath_only_fills_default_metadata(tmp_path):
    wav = tmp_path / "bare_track.wav"
    generate_tone(str(wav), duration_sec=1, freq_hz=440)

    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist([{"filepath": str(wav)}])
        pl = player.get_playlist()
        assert len(pl) == 1
        assert pl[0]["filename"] == "bare_track.wav"
        assert pl[0]["title"] == "bare_track.wav"
        assert pl[0]["artist"] == "Unknown Artist"
        assert pl[0]["genre"] == "Unknown"
        assert pl[0]["duration"] == 0
    finally:
        player.server.stop()
