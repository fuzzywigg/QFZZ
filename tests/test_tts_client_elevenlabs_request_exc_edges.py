"""TTSClient ElevenLabs RequestException is caught by synthesize → None."""

from unittest.mock import patch

import requests

from qfzz.dj.tts_client import TTSClient


def test_elevenlabs_request_exception_returns_none(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
    client = object.__new__(TTSClient)
    client.provider = "elevenlabs"
    client._client = {"api_key": "el-test"}

    with patch(
        "requests.post",
        side_effect=requests.exceptions.RequestException("timeout"),
    ):
        assert client.synthesize("hello radio") is None
