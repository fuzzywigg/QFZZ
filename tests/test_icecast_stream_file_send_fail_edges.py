"""IcecastClient.stream_file mid-send abort and IO exception edges."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

sys.modules.setdefault("shout", MagicMock())

from qfzz.streaming.icecast_client import (  # noqa: E402
    IcecastClient,
    IcecastConfig,
    IcecastState,
)


def test_stream_file_returns_false_when_send_audio_fails(tmp_path: Path):
    wav = tmp_path / "chunk.wav"
    wav.write_bytes(b"RIFF" + b"\x00" * 20)
    client = IcecastClient(IcecastConfig())
    client._shout = MagicMock()
    client._state = IcecastState.CONNECTED

    with patch.object(client, "send_audio", return_value=False) as send:
        assert client.stream_file(str(wav), chunk_size=8) is False
    send.assert_called()


def test_stream_file_io_error_returns_false(tmp_path: Path):
    wav = tmp_path / "broken.wav"
    wav.write_bytes(b"RIFF")
    client = IcecastClient(IcecastConfig())
    client._shout = MagicMock()
    client._state = IcecastState.CONNECTED

    with patch("builtins.open", mock_open()) as mopen:
        mopen.side_effect = OSError("disk read fail")
        assert client.stream_file(str(wav)) is False
