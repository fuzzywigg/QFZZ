"""Package LLMRouter skips unhealthy non-fallback then uses next healthy."""

from unittest.mock import MagicMock, patch

from qfzz.exceptions import LLMProviderError
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


def test_generate_skips_unhealthy_api_then_uses_fallback_mock():
    settings = _settings()
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        router = LLMRouter(config=settings)

    unhealthy = {
        "name": "SickAPI",
        "provider": MagicMock(),
        "priority": 1,
        "type": "api",
    }
    unhealthy["provider"].generate.side_effect = AssertionError("should skip")
    fallback = MagicMock()
    fallback.generate.return_value = "mock-ok"
    # Force unhealthy via health check returning False for non-fallback
    with patch.object(
        router, "_is_provider_healthy", side_effect=lambda info: info["type"] == "fallback"
    ):
        router.providers = [
            unhealthy,
            {"name": "Mock", "provider": fallback, "priority": 99, "type": "fallback"},
        ]
        result = router.generate("hello")

    assert result["success"] is True
    assert result["provider"] == "Mock"
    assert result["text"] == "mock-ok"


def test_generate_continues_after_llm_provider_error():
    settings = _settings()
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        router = LLMRouter(config=settings)

    boom = MagicMock()
    boom.generate.side_effect = LLMProviderError("transient")
    ok = MagicMock()
    ok.generate.return_value = "recovered"
    router.providers = [
        {"name": "Boom", "provider": boom, "priority": 1, "type": "api"},
        {"name": "Ok", "provider": ok, "priority": 2, "type": "api"},
    ]
    with patch.object(router, "_is_provider_healthy", return_value=True):
        result = router.generate("ping")
    assert result == {"text": "recovered", "provider": "Ok", "success": True}
