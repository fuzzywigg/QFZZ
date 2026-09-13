"""IcecastClient.get_stats reports connected after successful send_audio."""

from unittest.mock import MagicMock, Mock, patch

import qfzz.streaming.icecast_client as icecast_mod
from qfzz.streaming.icecast_client import IcecastClient, IcecastConfig, IcecastState


def test_get_stats_connected_after_send_audio():
    mock_shout = MagicMock()
    mock_instance = Mock()
    mock_shout.Shout.return_value = mock_instance
    mock_shout.SHOUT_AI_BITRATE = "bitrate"
    mock_shout.SHOUT_AI_SAMPLERATE = "samplerate"
    mock_shout.SHOUT_AI_CHANNELS = "channels"

    with (
        patch.object(icecast_mod, "SHOUT_AVAILABLE", True),
        patch.object(icecast_mod, "shout", mock_shout, create=True),
    ):
        client = IcecastClient(IcecastConfig())
        assert client.connect() is True
        assert client.send_audio(b"\x00\x01\x02\x03") is True
        stats = client.get_stats()
        assert stats["connected"] is True
        assert stats["bytes_sent"] >= 4
        assert client.get_state() == IcecastState.STREAMING
        client.disconnect()
