"""IcecastClient.connect with format=wav skips audio_info and still connects."""

import sys
from unittest.mock import MagicMock, Mock, patch

sys.modules.setdefault("shout", MagicMock())

import qfzz.streaming.icecast_client as icecast_mod  # noqa: E402
from qfzz.streaming.icecast_client import (  # noqa: E402
    IcecastClient,
    IcecastConfig,
    IcecastState,
)


def test_connect_wav_format_skips_audio_info_assignment():
    import shout as mock_shout

    mock_instance = Mock()
    mock_instance.format = None
    mock_instance.audio_info = "UNSET"
    mock_shout.Shout.return_value = mock_instance

    # Module may already be imported without shout (other streaming suites).
    config = IcecastConfig(format="wav", bitrate=128)
    with (
        patch.object(icecast_mod, "SHOUT_AVAILABLE", True),
        patch.object(icecast_mod, "shout", mock_shout, create=True),
    ):
        client = IcecastClient(config)
        assert client.connect() is True

    assert client.get_state() == IcecastState.CONNECTED
    # Neither mp3 nor ogg branch ran — format/audio_info left as shout defaults
    assert mock_instance.format is None or mock_instance.format != "mp3"
    assert mock_instance.audio_info == "UNSET"
    assert client._connection_time is not None
