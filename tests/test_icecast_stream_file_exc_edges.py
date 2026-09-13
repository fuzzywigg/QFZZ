"""Icecast stream_file I/O exception + __del__ cleanup edges."""

from unittest.mock import MagicMock, patch

from qfzz.streaming.icecast_client import IcecastClient, IcecastState


def test_stream_file_open_exception_returns_false(tmp_path):
    audio = tmp_path / "track.mp3"
    audio.write_bytes(b"12345")
    client = IcecastClient()
    client._shout = MagicMock()
    client._state = IcecastState.CONNECTED
    with patch("builtins.open", side_effect=OSError("read fail")):
        assert client.stream_file(str(audio)) is False


def test_del_calls_disconnect_without_raise():
    client = IcecastClient()
    client.disconnect = MagicMock()
    client.stop_streaming_thread = MagicMock()
    client.__del__()
    client.stop_streaming_thread.assert_called_once()
    client.disconnect.assert_called_once()
