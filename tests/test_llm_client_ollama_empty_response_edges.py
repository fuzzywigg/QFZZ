"""OllamaClient.generate returns empty string when response field is missing."""

from unittest.mock import MagicMock, patch

from qfzz.llm.client import OllamaClient


def test_ollama_generate_missing_response_field_returns_empty():
    tags_resp = MagicMock()
    tags_resp.status = 200
    tags_resp.__enter__.return_value = tags_resp
    tags_resp.__exit__.return_value = False

    gen_resp = MagicMock()
    gen_resp.read.return_value = b"{}"
    gen_resp.__enter__.return_value = gen_resp
    gen_resp.__exit__.return_value = False

    with patch("qfzz.llm.client.urllib.request.urlopen", side_effect=[tags_resp, gen_resp]):
        client = OllamaClient(base_url="http://localhost:11434")
        assert client.is_available() is True
        assert client.generate("spin") == ""
