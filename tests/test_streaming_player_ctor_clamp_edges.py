"""MusicPlayer constructor clamps for buffer/prefetch/reconnect."""

from qfzz.streaming.player import MusicPlayer


def test_ctor_clamps_zero_and_negative_tuning(tmp_path):
    player = MusicPlayer(
        content_dir=str(tmp_path),
        port=0,
        buffer_seconds=0,
        prefetch_count=0,
        reconnect_max_attempts=0,
    )
    try:
        assert player._buffer_seconds == 2
        assert player._prefetch_count == 1
        assert player._reconnect_max_attempts == 1
        status = player.get_stream_status()
        assert status["buffer_seconds"] == 2
        assert status["reconnect"]["max_attempts"] == 1
    finally:
        player.server.stop()


def test_ctor_clamps_negative_values(tmp_path):
    player = MusicPlayer(
        content_dir=str(tmp_path),
        port=0,
        buffer_seconds=-5,
        prefetch_count=-2,
        reconnect_max_attempts=-9,
    )
    try:
        assert player._buffer_seconds == 2
        assert player._prefetch_count == 1
        assert player._reconnect_max_attempts == 1
    finally:
        player.server.stop()
