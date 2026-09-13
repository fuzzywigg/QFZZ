"""TTSClient OpenAI constructor Exception soft-fail (not ImportError)."""

from unittest.mock import patch

from qfzz.dj.tts_client import TTSClient


def test_openai_ctor_exception_clears_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with patch("openai.OpenAI", side_effect=RuntimeError("ctor fail")):
        client = TTSClient(provider="openai")
        assert client._client is None
        assert client.is_available() is False
