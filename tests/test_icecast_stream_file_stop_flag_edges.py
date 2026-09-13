"""IcecastClient.stream_file exits cleanly when stop flag is set mid-loop."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.modules.setdefault("shout", MagicMock())

from qfzz.streaming.icecast_client import (  # noqa: E402
    IcecastClient,
    IcecastConfig,
    IcecastState,
)


def test_stream_file_stop_flag_returns_true_without_send_failure(tmp_path: Path):
    wav = tmp_path / "long.wav"
    wav.write_bytes(b"RIFF" + b"\x00" * 64)
    client = IcecastClient(IcecastConfig())
    client._shout = MagicMock()
    client._state = IcecastState.CONNECTED

    chunks = [b"aaaa", b"bbbb", b"cccc"]

    def fake_read(size=-1):
        if chunks:
            return chunks.pop(0)
        return b""

    handle = MagicMock()
    handle.read.side_effect = fake_read
    handle.__enter__.return_value = handle
    handle.__exit__.return_value = False

    send_calls = {"n": 0}

    def send_and_stop(_data: bytes) -> bool:
        send_calls["n"] += 1
        if send_calls["n"] == 1:
            client._stop_flag.set()
        return True

    with patch("builtins.open", return_value=handle):
        with patch.object(client, "send_audio", side_effect=send_and_stop) as send:
            assert client.stream_file(str(wav), chunk_size=4) is True
    assert send.call_count == 1
