"""Gemini/Ollama client init and availability edges (mocked imports/network)."""

from unittest.mock import MagicMock, patch

from qfzz.llm.client import GeminiClient, OllamaClient


def test_gemini_init_import_failure_marks_unavailable():
    with patch.dict("sys.modules", {"google.generativeai": None}):
        # Force ImportError path by making import raise
        import builtins

        real_import = builtins.__import__

        def boom(name, *args, **kwargs):
            if name == "google.generativeai" or name.startswith("google.generativeai"):
                raise ImportError("no gemini")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=boom):
            client = GeminiClient(api_key="sk-test")
    assert client.is_available() is False
    assert client.generate("hi") == "Gemini API is not available."


def test_gemini_generate_without_system_prompt():
    client = object.__new__(GeminiClient)
    client.api_key = "sk-test"
    client.model_name = "gemini-pro"
    client._available = True
    model = MagicMock()
    model.generate_content.return_value = MagicMock(text="pong")
    client.model = model

    out = client.generate("ping")
    assert out == "pong"
    model.generate_content.assert_called_once()
    arg = model.generate_content.call_args[0][0]
    assert "ping" in arg


def test_ollama_tags_non_200_stays_unavailable():
    resp = MagicMock()
    resp.status = 500
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)

    with patch("qfzz.llm.client.urllib.request.urlopen", return_value=resp):
        client = OllamaClient(base_url="http://127.0.0.1:9")
    assert client.is_available() is False
    assert client.generate("x") == "Ollama is not connected."
