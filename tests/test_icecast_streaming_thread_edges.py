"""Edge coverage for IcecastClient disconnected paths and streaming thread (mocked shout).

Isolates shout via per-test patches so it does not pollute tests/test_icecast_client.py.
"""

import threading
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from qfzz.streaming.icecast_client import IcecastClient, IcecastConfig, IcecastState


@pytest.fixture
def config():
    return IcecastConfig(host="localhost", port=8000, password="test", mount="/test")


@pytest.fixture
def shout_env():
    """Patch shout + SHOUT_AVAILABLE for the duration of one test only."""
    mock_shout = MagicMock()
    mock_instance = Mock()
    mock_shout.Shout.return_value = mock_instance
    mock_shout.Metadata.return_value = Mock()
    mock_shout.SHOUT_AI_BITRATE = "bitrate"
    mock_shout.SHOUT_AI_SAMPLERATE = "samplerate"
    mock_shout.SHOUT_AI_CHANNELS = "channels"
    with patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True):
        with patch("qfzz.streaming.icecast_client.shout", mock_shout):
            yield mock_shout, mock_instance


def test_connect_ogg_format(config, shout_env):
    _, mock_instance = shout_env
    config.format = "ogg"
    client = IcecastClient(config)
    assert client.connect() is True
    assert mock_instance.format == "ogg"
    client.disconnect()


def test_metadata_and_send_when_disconnected(config):
    client = IcecastClient(config)
    client._state = IcecastState.DISCONNECTED
    client._shout = None
    assert client.update_metadata({"title": "T", "artist": "A"}) is False
    assert client.send_audio(b"abc") is False


def test_disconnect_close_raises(config, shout_env):
    _, mock_instance = shout_env
    mock_instance.close.side_effect = RuntimeError("close fail")
    client = IcecastClient(config)
    assert client.connect() is True
    client.disconnect()
    assert client._state == IcecastState.DISCONNECTED
    assert client._shout is None


def test_streaming_thread_already_running_and_stop(tmp_path: Path, config, shout_env):
    audio = tmp_path / "t.wav"
    audio.write_bytes(b"RIFF")
    client = IcecastClient(config)
    assert client.connect() is True

    hold = threading.Event()
    started = threading.Event()
    calls = {"n": 0}

    def playlist_callback():
        calls["n"] += 1
        started.set()
        hold.wait(timeout=2.0)
        client._stop_flag.set()
        return {"title": "Ok", "artist": "A", "filepath": str(audio)}

    with patch("qfzz.streaming.icecast_client.time.sleep", return_value=None):
        assert client.start_streaming_thread(playlist_callback) is True
        assert started.wait(timeout=1.0)
        # Thread still alive → second start must fail
        assert client.start_streaming_thread(playlist_callback) is False
        hold.set()
        client.stop_streaming_thread()
    assert calls["n"] >= 1
    client.disconnect()


def test_streaming_loop_empty_missing_and_exception(tmp_path: Path, config, shout_env):
    client = IcecastClient(config)
    client._stop_flag.clear()
    sequence = [
        None,
        {"title": "Missing", "filepath": str(tmp_path / "nope.wav")},
        RuntimeError("callback boom"),
    ]
    idx = {"i": 0}

    def playlist_callback():
        i = idx["i"]
        idx["i"] += 1
        if i >= len(sequence):
            client._stop_flag.set()
            return None
        item = sequence[i]
        if isinstance(item, Exception):
            client._stop_flag.set()
            raise item
        return item

    with patch("qfzz.streaming.icecast_client.time.sleep", return_value=None):
        client._streaming_loop(playlist_callback)
    assert idx["i"] >= 2
