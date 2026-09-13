"""TTS client import-fail and exception synthesis edges (no real APIs)."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_openai_import_error_unavailable(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "openai" or name.startswith("openai."):
            raise ImportError("no openai")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        client = TTSClient(provider="openai")
        assert client._client is None
        assert client.is_available() is False


def test_elevenlabs_missing_key_unavailable(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    client = TTSClient(provider="elevenlabs")
    assert client.is_available() is False
    assert client.synthesize("hi") is None


def test_google_import_error_unavailable():
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "google.cloud" or name.startswith("google"):
            raise ImportError("no google")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        client = TTSClient(provider="google")
        assert client._client is None
        assert client.is_available() is False


def test_openai_synthesize_exception_returns_none(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    mock_client = MagicMock()
    mock_client.audio.speech.create.side_effect = RuntimeError("api down")
    fake_openai = MagicMock()
    fake_openai.OpenAI.return_value = mock_client
    with patch.dict("sys.modules", {"openai": fake_openai}):
        client = TTSClient(provider="openai")
        assert client.synthesize("hello") is None


def test_mystery_provider_with_client_returns_none():
    client = object.__new__(TTSClient)
    client.provider = "mystery"
    client._client = object()
    assert client.synthesize("hello") is None
