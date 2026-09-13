"""Empty playlist / wrong-state / non-recoverable error edges for MusicPlayer."""

from pathlib import Path

from qfzz.streaming.player import MusicPlayer, PlayerState


def test_empty_playlist_controls_return_false(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, reconnect_max_attempts=1)
    try:
        player._playlist = []  # bypass auto test content for empty-path assertions
        assert player.play() is False
        assert player.next_track() is False
        assert player.previous_track() is False
        assert player.pause() is False
        assert player.resume() is False
        assert player.seek(1) is False
        assert "#EXT-X-ENDLIST" in player.get_hls_manifest()
    finally:
        player.server.stop()


def test_invalid_index_and_wrong_state(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "intro.wav", "duration": 10}]
        )
        assert player.play(99) is False
        assert player.pause() is False
        assert player.play(0) is True
        assert player.resume() is False  # already playing
        assert player.pause() is True
        assert player.pause() is False  # already paused
    finally:
        player.stop()
        player.server.stop()


def test_non_recoverable_stream_error_and_no_dataset_manager(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, reconnect_max_attempts=1)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "intro.wav", "duration": 8}]
        )
        assert player.play() is True
        assert player.report_stream_error("hard fail", recoverable=False) is False
        assert player.get_state() == PlayerState.STOPPED

        assert player.load_playlist_from_datasets() == 0
        player.set_dj_message("edge")
        player.set_ledger_stats({"height": 7, "status": "ok"})
        from qfzz.streaming.server import AudioRequestHandler

        assert AudioRequestHandler.DJ_MESSAGE["message"] == "edge"
        assert AudioRequestHandler.LEDGER_STATS["height"] == 7
    finally:
        player.stop()
        player.server.stop()


def test_recoverable_error_then_exhaust(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, reconnect_max_attempts=1)
    try:
        player.load_playlist(
            [{"title": "A", "artist": "X", "filename": "intro.wav", "duration": 5}]
        )
        assert player.play() is True
        assert player.report_stream_error("blip", recoverable=True) is True
        assert player.get_state() == PlayerState.PLAYING
        assert player.report_stream_error("again", recoverable=True) is False
        assert player.get_state() == PlayerState.STOPPED
    finally:
        player.stop()
        player.server.stop()
