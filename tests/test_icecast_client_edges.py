"""Edge paths for IcecastClient: unavailable shout, ogg, metadata/send failures, threads."""

import sys
import time
from unittest.mock import MagicMock, Mock, patch

# Ensure shout is importable as a mock module before client use.
sys.modules.setdefault("shout", MagicMock())

from qfzz.streaming.icecast_client import (  # noqa: E402
    IcecastClient,
    IcecastConfig,
    IcecastState,
)


def test_init_sets_error_when_shout_unavailable():
    with patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", False):
        client = IcecastClient(IcecastConfig())
        assert client.get_state() == IcecastState.ERROR
        assert client.connect() is False


def test_connect_ogg_format_and_disconnect_close_error():
    import shout as mock_shout

    mock_instance = Mock()
    mock_shout.Shout.return_value = mock_instance
    mock_shout.SHOUT_AI_BITRATE = "bitrate"
    mock_shout.SHOUT_AI_SAMPLERATE = "samplerate"
    mock_shout.SHOUT_AI_CHANNELS = "channels"

    config = IcecastConfig(format="ogg", bitrate=160, public=True)
    with patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True):
        client = IcecastClient(config)
        assert client.connect() is True
        assert mock_instance.format == "ogg"
        assert client.get_state() == IcecastState.CONNECTED

        mock_instance.close.side_effect = RuntimeError("close fail")
        client.disconnect()
        assert client.get_state() == IcecastState.DISCONNECTED
        assert client._shout is None


def test_metadata_and_send_audio_disconnected_and_exceptions():
    client = IcecastClient(IcecastConfig())
    client._state = IcecastState.DISCONNECTED
    client._shout = None
    assert client.update_metadata({"title": "T", "artist": "A"}) is False
    assert client.send_audio(b"abc") is False

    import shout as mock_shout

    mock_instance = Mock()
    mock_instance.set_metadata.side_effect = RuntimeError("meta boom")
    mock_instance.send.side_effect = RuntimeError("send boom")
    mock_shout.Metadata.return_value = Mock()

    client._shout = mock_instance
    client._state = IcecastState.CONNECTED
    assert client.update_metadata({"title": "T"}) is False

    assert client.send_audio(b"xyz") is False
    assert client.get_state() == IcecastState.ERROR


def test_stream_file_missing_and_disconnected(tmp_path):
    client = IcecastClient(IcecastConfig())
    missing = str(tmp_path / "nope.mp3")
    assert client.stream_file(missing) is False

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"\x00" * 20)
    client._state = IcecastState.DISCONNECTED
    client._shout = None
    assert client.stream_file(str(audio)) is False


def test_streaming_thread_start_stop_and_already_running(tmp_path):
    audio = tmp_path / "t.mp3"
    audio.write_bytes(b"\x01" * 64)

    client = IcecastClient(IcecastConfig())
    client._state = IcecastState.CONNECTED
    client._shout = Mock()
    client._shout.send = Mock()
    client._shout.sync = Mock()

    calls = {"n": 0}

    def playlist_callback():
        calls["n"] += 1
        if calls["n"] == 1:
            return None
        if calls["n"] == 2:
            return {"title": "X", "artist": "Y", "filepath": str(tmp_path / "missing.mp3")}
        if calls["n"] == 3:
            return {"title": "Ok", "artist": "Y", "filepath": str(audio)}
        client._stop_flag.set()
        return None

    with patch.object(client, "update_metadata", return_value=True):
        assert client.start_streaming_thread(playlist_callback) is True
        assert client.start_streaming_thread(playlist_callback) is False
        time.sleep(0.35)
        client.stop_streaming_thread()
        assert calls["n"] >= 1


def test_get_stats_disconnected_uptime_none():
    client = IcecastClient(IcecastConfig(host="h", port=9, mount="/m"))
    client._state = IcecastState.DISCONNECTED
    client._connection_time = None
    stats = client.get_stats()
    assert stats["connected"] is False
    assert stats["uptime_seconds"] is None
    assert stats["server"] == "h:9/m"
    assert stats["bytes_sent"] == 0
