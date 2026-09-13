"""qfzz.llm.router Ollama ctor soft-fail (Mock remains; complements HF/Together/Gemini suite)."""

from unittest.mock import MagicMock, patch

from qfzz.llm.router import LLMRouter


def _settings():
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = None
    settings.llm.together_api_key = None
    settings.llm.huggingface_api_key = None
    settings.llm.gemini_api_key = None
    return settings


def test_ollama_ctor_failure_keeps_mock_only():
    settings = _settings()
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient", side_effect=RuntimeError("no ollama")),
    ):
        router = LLMRouter(config=settings)
        names = [p["name"] for p in router.providers]
    assert "Ollama" not in names
    assert names == ["Mock"]
    assert router.providers[0]["priority"] == 99
