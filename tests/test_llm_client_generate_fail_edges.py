"""LLM client generate failure / unavailable / system-prompt edges (mocked)."""

from unittest.mock import MagicMock, patch

from qfzz.llm.client import GeminiClient, MockLLMClient, OllamaClient


def test_mock_llm_always_available_and_echoes_prompt():
    client = MockLLMClient()
    assert client.is_available() is True
    out = client.generate("spin a track")
    assert "spin a track" in out
    assert "placeholder DJ" in out


def test_ollama_generate_urlopen_error_returns_error_string():
    client = object.__new__(OllamaClient)
    client.model = "llama3"
    client.base_url = "http://127.0.0.1:9"
    client._available = True

    with patch(
        "qfzz.llm.client.urllib.request.urlopen",
        side_effect=OSError("connection refused"),
    ):
        out = client.generate("hello", system_prompt="be brief")

    assert out.startswith("Error generating response:")
    assert "connection refused" in out


def test_ollama_generate_success_reads_response_field():
    client = object.__new__(OllamaClient)
    client.model = "llama3"
    client.base_url = "http://127.0.0.1:9"
    client._available = True

    payload = b'{"response":"quantum mix"}'
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)

    with patch("qfzz.llm.client.urllib.request.urlopen", return_value=resp):
        out = client.generate("hi")

    assert out == "quantum mix"


def test_gemini_generate_exception_and_system_prompt_prepend():
    client = object.__new__(GeminiClient)
    client.api_key = "sk-test"
    client.model_name = "gemini-pro"
    client._available = True
    model = MagicMock()
    model.generate_content.side_effect = RuntimeError("quota")
    client.model = model

    out = client.generate("ping", system_prompt="stay on brand")
    assert out.startswith("Error generating response:")
    assert "quota" in out
    arg = model.generate_content.call_args[0][0]
    assert arg.startswith("System: stay on brand")
    assert "User: ping" in arg
