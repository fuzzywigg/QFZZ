"""Edge coverage for Gemini/Ollama client init and generate failure paths."""

import json
from unittest.mock import MagicMock, patch

from qfzz.llm.client import GeminiClient, MockLLMClient, OllamaClient


def test_mock_llm_accepts_kwargs():
    client = MockLLMClient()
    assert "hello" in client.generate("hello", temperature=0.1, max_tokens=5)
    assert client.is_available() is True


def test_ollama_status_not_200_unavailable():
    resp = MagicMock()
    resp.status = 503
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    with patch("qfzz.llm.client.urllib.request.urlopen", return_value=resp):
        client = OllamaClient(base_url="http://localhost:9")
    assert client.is_available() is False
    assert client.generate("hi") == "Ollama is not connected."


def test_ollama_generate_with_system_and_missing_response_key():
    tags = MagicMock()
    tags.status = 200
    tags.__enter__ = MagicMock(return_value=tags)
    tags.__exit__ = MagicMock(return_value=False)

    gen_body = json.dumps({"done": True}).encode()
    gen = MagicMock()
    gen.read.return_value = gen_body
    gen.__enter__ = MagicMock(return_value=gen)
    gen.__exit__ = MagicMock(return_value=False)

    with patch("qfzz.llm.client.urllib.request.urlopen", side_effect=[tags, gen]):
        client = OllamaClient()
        assert client.is_available() is True
        out = client.generate("ping", system_prompt="Be brief")
    assert out == ""


def test_ollama_generate_exception_returns_error_string():
    tags = MagicMock()
    tags.status = 200
    tags.__enter__ = MagicMock(return_value=tags)
    tags.__exit__ = MagicMock(return_value=False)

    with patch("qfzz.llm.client.urllib.request.urlopen", side_effect=[tags, OSError("down")]):
        client = OllamaClient()
        msg = client.generate("x")
    assert msg.startswith("Error generating response:")


def test_gemini_configure_exception_marks_unavailable():
    with patch.dict("sys.modules", {"google.generativeai": MagicMock()}):
        import google.generativeai as genai

        genai.configure.side_effect = RuntimeError("bad key")
        client = GeminiClient(api_key="fake")
    assert client.is_available() is False
    assert client.generate("hi") == "Gemini API is not available."


def test_gemini_generate_prepends_system_and_handles_error():
    model = MagicMock()
    model.generate_content.return_value = MagicMock(text="ok")
    genai = MagicMock()
    genai.GenerativeModel.return_value = model
    with patch.dict("sys.modules", {"google.generativeai": genai}):
        # Re-import path used inside __init__
        client = GeminiClient(api_key="k")
        # Force available path if configure succeeded via MagicMock
        client._available = True
        client.model = model
        assert client.generate("user", system_prompt="sys") == "ok"
        model.generate_content.assert_called_once()
        assert "System: sys" in model.generate_content.call_args[0][0]

        model.generate_content.side_effect = RuntimeError("api")
        err = client.generate("user")
        assert err.startswith("Error generating response:")
