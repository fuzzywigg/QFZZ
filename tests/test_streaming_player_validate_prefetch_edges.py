"""MusicPlayer validate / prefetch wrap / history-cap / seek edges."""

from qfzz.audio.generator import generate_tone
from qfzz.streaming.player import MusicPlayer, PlayerState


def test_validate_absolute_filepath(tmp_path):
    content = tmp_path / "content"
    content.mkdir()
    outside = tmp_path / "outside.wav"
    generate_tone(str(outside), duration_sec=1, freq_hz=440)

    player = MusicPlayer(content_dir=str(content), port=0)
    try:
        player.load_playlist(
            [{"title": "Abs", "filepath": str(outside), "duration": 1}]
        )
        pl = player.get_playlist()
        assert len(pl) == 1
        assert pl[0]["filename"] == "outside.wav"
        assert pl[0]["filepath"] == str(outside)
    finally:
        player.server.stop()


def test_validate_skips_track_without_path_keys(tmp_path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist([{"title": "NoPath", "artist": "X"}])
        assert player.get_playlist() == []
    finally:
        player.server.stop()


def test_add_track_missing_file_is_noop(tmp_path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        before = len(player.get_playlist())
        player.add_track({"title": "Ghost", "filename": "missing.wav"})
        assert len(player.get_playlist()) == before
    finally:
        player.server.stop()


def test_playback_history_capped_at_100(tmp_path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        for i in range(105):
            player._record_playback_event("tick", {"i": i})
        hist = player.get_playback_history(limit=200)
        assert len(hist) == 100
        assert hist[0]["metadata"]["i"] == 5
        assert hist[-1]["metadata"]["i"] == 104
    finally:
        player.server.stop()


def test_prefetch_wraps_around_playlist(tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    generate_tone(str(a), duration_sec=1, freq_hz=440)
    generate_tone(str(b), duration_sec=1, freq_hz=554)

    player = MusicPlayer(content_dir=str(tmp_path), port=0, prefetch_count=2)
    try:
        player.load_playlist(
            [
                {"title": "A", "filename": "a.wav", "duration": 1},
                {"title": "B", "filename": "b.wav", "duration": 1},
            ]
        )
        assert player.play(0) is True
        status = player.get_stream_status()
        titles = [t["title"] for t in status["prefetch_tracks"]]
        assert titles == ["B", "A"]
    finally:
        player.server.stop()


def test_seek_allows_zero_when_duration_zero(tmp_path):
    wav = tmp_path / "z.wav"
    generate_tone(str(wav), duration_sec=1, freq_hz=220)
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist([{"title": "Z", "filename": "z.wav", "duration": 0}])
        player.play(0)
        assert player.seek(0) is True
        assert player.seek(1) is False
        assert player.get_state() == PlayerState.PLAYING
    finally:
        player.server.stop()
