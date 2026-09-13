"""TTSClient.synthesize short-circuits whitespace before provider call."""

from unittest.mock import MagicMock

from qfzz.dj.tts_client import TTSClient


def test_whitespace_only_skips_provider_when_client_ready():
    client = object.__new__(TTSClient)
    client.provider = "openai"
    mock_api = MagicMock()
    client._client = mock_api

    assert client.synthesize("\t  \n") is None
    mock_api.audio.speech.create.assert_not_called()
