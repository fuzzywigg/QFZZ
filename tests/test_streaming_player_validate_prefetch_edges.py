"""Edge coverage for MusicPlayer track validation, prefetch, and history cap."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer


def _wav(tmp_path: Path, name: str = "a.wav") -> Path:
    p = tmp_path / name
    p.write_bytes(b"RIFF....WAVEfmt ")
    return p


def test_validate_tracks_skips_missing_and_fills_defaults(tmp_path: Path):
    good = _wav(tmp_path, "good.wav")
    abs_wav = _wav(tmp_path, "abs.wav")
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        validated = player._validate_tracks(
            [
                {},  # no filename/filepath
                {"filename": "missing.wav"},
                {"filename": "good.wav"},
                {"filepath": str(abs_wav)},
                {"filepath": "good.wav", "title": "Custom"},
            ]
        )
        assert len(validated) == 3
        by_name = {t["filename"]: t for t in validated}
        assert by_name["good.wav"]["artist"] == "Unknown Artist"
        assert by_name["good.wav"]["genre"] == "Unknown"
        assert by_name["abs.wav"]["filepath"] == str(abs_wav)
        assert any(t.get("title") == "Custom" for t in validated)
        assert all(Path(t["filepath"]).is_file() for t in validated)
        assert good.name in by_name
    finally:
        player.server.stop()


def test_playback_history_cap_and_limit(tmp_path: Path):
    _wav(tmp_path, "intro.wav")
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "intro.wav", "duration": 5}]
        )
        player.play(0)
        for i in range(110):
            player._record_playback_event("tick", {"i": i})
        assert len(player._playback_history) == 100
        hist = player.get_playback_history(limit=5)
        assert len(hist) == 5
        assert hist[-1]["metadata"]["i"] == 109
    finally:
        player.stop()
        player.server.stop()


def test_prefetch_empty_and_wraparound(tmp_path: Path):
    for name in ("a.wav", "b.wav", "c.wav"):
        _wav(tmp_path, name)
    player = MusicPlayer(content_dir=str(tmp_path), port=0, prefetch_count=2)
    try:
        player._playlist = []
        player._current_index = -1
        player._compute_prefetch_queue()
        assert player._prefetch_queue == []

        player.load_playlist(
            [
                {"filename": "a.wav", "title": "A", "artist": "X", "duration": 1},
                {"filename": "b.wav", "title": "B", "artist": "X", "duration": 1},
                {"filename": "c.wav", "title": "C", "artist": "X", "duration": 1},
            ]
        )
        player.play(2)  # last track
        player._compute_prefetch_queue()
        titles = [t["title"] for t in player._prefetch_queue]
        assert titles == ["A", "B"]  # wraparound
    finally:
        player.stop()
        player.server.stop()
