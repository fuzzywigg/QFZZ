"""Expanded MusicPlayer unit coverage for controls and validation."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer, PlayerState


def test_music_player_controls_and_playlist_info(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, reconnect_max_attempts=1)
    try:
        # _ensure_test_content creates intro.wav and test_tone.wav
        player.load_playlist(
            [
                {"title": "A", "artist": "X", "filename": "intro.wav", "duration": 10},
                {"title": "B", "artist": "Y", "filename": "test_tone.wav", "duration": 12},
            ]
        )
        assert player.play() is True
        assert player.is_playing() is True
        assert player.pause() is True
        assert player.is_paused() is True
        assert player.resume() is True
        assert player.next_track() is True
        assert player.get_current_track()["title"] == "B"
        assert player.previous_track() is True
        assert player.get_current_track()["title"] == "A"
        assert player.set_volume(0.5) is True
        assert player.get_volume() == 0.5
        assert player.seek(3) is True
        assert player.get_position() == 3
        assert player.set_volume(2.0) is False
        assert player.seek(999) is False

        player.set_dj_message("welcome")
        player.set_ledger_stats({"blocks": 1})
        info = player.get_playlist_info()
        assert info["track_count"] == 2
        assert info["total_duration"] == 22
        assert player.get_stream_url("intro.wav").endswith("/intro.wav")
        manifest = player.get_hls_manifest()
        assert "#EXTM3U" in manifest
        player.stop()
        assert player.is_stopped() is True
        assert player.get_state() == PlayerState.STOPPED
    finally:
        player.server.stop()


def test_music_player_rejects_invalid_tracks(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [
                {"title": "Ok", "artist": "A", "filename": "intro.wav", "duration": 5},
                {"title": "Bad"},  # missing filename
                {"title": "Missing", "filename": "nope.wav"},  # file absent
            ]
        )
        playlist = player.get_playlist()
        assert len(playlist) == 1
        assert playlist[0]["filename"] == "intro.wav"
        player.add_track(
            {"title": "Extra", "artist": "B", "filename": "test_tone.wav", "duration": 4}
        )
        assert len(player.get_playlist()) == 2
        player.add_track({"title": "Reject", "filename": "absent.wav"})
        assert len(player.get_playlist()) == 2
    finally:
        player.server.stop()


def test_music_player_history_after_play(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "intro.wav", "duration": 5}]
        )
        assert player.play() is True
        history = player.get_playback_history(limit=5)
        assert isinstance(history, list)
        assert len(history) >= 1
    finally:
        player.stop()
        player.server.stop()
