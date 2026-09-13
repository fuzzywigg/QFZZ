"""Tests for llm client mocks and Ollama HTTP paths."""

from unittest.mock import MagicMock, patch

from qfzz.llm.client import GeminiClient, MockLLMClient, OllamaClient


class TestMockLLMClient:
    def test_generate_echoes_prompt(self):
        client = MockLLMClient()
        assert client.is_available() is True
        text = client.generate("hello hive")
        assert "hello hive" in text
        assert "placeholder DJ" in text


class TestOllamaClient:
    def test_unavailable_when_tags_fail(self):
        with patch("qfzz.llm.client.urllib.request.urlopen", side_effect=OSError("down")):
            client = OllamaClient(base_url="http://localhost:9")
            assert client.is_available() is False
            assert client.generate("hi") == "Ollama is not connected."

    def test_generate_success(self):
        tags_resp = MagicMock()
        tags_resp.status = 200
        tags_resp.__enter__.return_value = tags_resp
        tags_resp.__exit__.return_value = False

        gen_resp = MagicMock()
        gen_resp.read.return_value = b'{"response": "spin that track"}'
        gen_resp.__enter__.return_value = gen_resp
        gen_resp.__exit__.return_value = False

        with patch("qfzz.llm.client.urllib.request.urlopen", side_effect=[tags_resp, gen_resp]):
            client = OllamaClient(base_url="http://localhost:11434")
            assert client.is_available() is True
            assert client.generate("play jazz") == "spin that track"

    def test_generate_handles_http_error(self):
        tags_resp = MagicMock()
        tags_resp.status = 200
        tags_resp.__enter__.return_value = tags_resp
        tags_resp.__exit__.return_value = False

        with patch(
            "qfzz.llm.client.urllib.request.urlopen",
            side_effect=[tags_resp, OSError("boom")],
        ):
            client = OllamaClient(base_url="http://localhost:11434")
            out = client.generate("x")
            assert out.startswith("Error generating response:")


class TestGeminiClient:
    def test_unavailable_generate(self):
        client = object.__new__(GeminiClient)
        client.api_key = "x"
        client.model_name = "gemini-pro"
        client._available = False
        assert client.is_available() is False
        assert client.generate("hi") == "Gemini API is not available."

    def test_generate_with_mocked_model(self):
        client = object.__new__(GeminiClient)
        client.api_key = "k"
        client.model_name = "gemini-pro"
        client._available = True
        model = MagicMock()
        model.generate_content.return_value = MagicMock(text="ok")
        client.model = model
        assert client.generate("ping", system_prompt="be brief") == "ok"
        args = model.generate_content.call_args[0][0]
        assert "System: be brief" in args
        assert "User: ping" in args

    def test_generate_exception_path(self):
        client = object.__new__(GeminiClient)
        client._available = True
        model = MagicMock()
        model.generate_content.side_effect = RuntimeError("quota")
        client.model = model
        out = client.generate("x")
        assert out.startswith("Error generating response:")
