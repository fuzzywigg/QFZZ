"""IcecastClient _streaming_loop empty track / missing filepath edges."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.modules.setdefault("shout", MagicMock())

from qfzz.streaming.icecast_client import IcecastClient, IcecastConfig  # noqa: E402


def test_streaming_loop_none_then_missing_filepath(tmp_path: Path):
    client = IcecastClient(IcecastConfig())
    client._state = client.get_state()  # keep default
    calls = {"n": 0}

    def callback():
        calls["n"] += 1
        if calls["n"] == 1:
            return None
        if calls["n"] == 2:
            return {"title": "Ghost", "filepath": str(tmp_path / "missing.wav")}
        client._stop_flag.set()
        return None

    slept = []

    def fake_sleep(sec):
        slept.append(sec)

    with (
        patch("qfzz.streaming.icecast_client.time.sleep", side_effect=fake_sleep),
        patch.object(client, "update_metadata", return_value=True),
        patch.object(client, "stream_file", return_value=True) as stream_file,
    ):
        client._streaming_loop(callback)

    assert None in [None]  # loop exited via stop
    assert 1.0 in slept
    stream_file.assert_not_called()
    assert calls["n"] >= 3


def test_streaming_loop_streams_existing_file(tmp_path: Path):
    wav = tmp_path / "ok.wav"
    wav.write_bytes(b"RIFF")
    client = IcecastClient(IcecastConfig())
    calls = {"n": 0}

    def callback():
        calls["n"] += 1
        if calls["n"] == 1:
            return {"title": "Ok", "filepath": str(wav)}
        client._stop_flag.set()
        return None

    with (
        patch("qfzz.streaming.icecast_client.time.sleep", return_value=None),
        patch.object(client, "update_metadata", return_value=True) as meta,
        patch.object(client, "stream_file", return_value=True) as stream_file,
    ):
        client._streaming_loop(callback)

    meta.assert_called()
    stream_file.assert_called_once_with(str(wav))
