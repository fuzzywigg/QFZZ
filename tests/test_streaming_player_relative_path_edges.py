"""Relative filepath resolution under MusicPlayer._validate_tracks."""

from qfzz.audio.generator import generate_tone
from qfzz.streaming.player import MusicPlayer


def test_validate_relative_nested_filepath(tmp_path):
    nested = tmp_path / "sub"
    nested.mkdir()
    wav = nested / "rel.wav"
    generate_tone(str(wav), duration_sec=1, freq_hz=440)

    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "Rel", "filepath": "sub/rel.wav", "duration": 1}]
        )
        pl = player.get_playlist()
        assert len(pl) == 1
        assert pl[0]["filename"] == "rel.wav"
        assert pl[0]["filepath"] == str(wav)
        assert pl[0]["title"] == "Rel"
    finally:
        player.server.stop()


def test_validate_relative_missing_filepath_skipped(tmp_path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "Ghost", "filepath": "no/such.wav", "duration": 1}]
        )
        assert player.get_playlist() == []
    finally:
        player.server.stop()
