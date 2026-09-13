"""IcecastClient _streaming_loop exception recovery (sleep 5s) edges."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.modules.setdefault("shout", MagicMock())

from qfzz.streaming.icecast_client import IcecastClient, IcecastConfig  # noqa: E402


def test_streaming_loop_callback_exception_sleeps_five_then_continues(tmp_path: Path):
    client = IcecastClient(IcecastConfig())
    calls = {"n": 0}
    slept = []

    def callback():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("playlist boom")
        client._stop_flag.set()
        return None

    def fake_sleep(sec):
        slept.append(sec)

    with (
        patch("qfzz.streaming.icecast_client.time.sleep", side_effect=fake_sleep),
        patch.object(client, "update_metadata", return_value=True),
        patch.object(client, "stream_file", return_value=True) as stream_file,
    ):
        client._streaming_loop(callback)

    assert 5.0 in slept
    stream_file.assert_not_called()
    assert calls["n"] >= 2
