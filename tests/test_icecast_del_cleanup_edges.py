"""IcecastClient __del__ cleanup edge (stream_file IO covered in send_fail suite)."""

from unittest.mock import MagicMock

from qfzz.streaming.icecast_client import IcecastClient


def test_del_calls_disconnect_without_raise():
    client = IcecastClient()
    client.disconnect = MagicMock()
    client.stop_streaming_thread = MagicMock()
    client.__del__()
    client.stop_streaming_thread.assert_called_once()
    client.disconnect.assert_called_once()
