"""Tests for qfzz.llm.router.LLMRouter provider selection."""

from unittest.mock import MagicMock, patch

from qfzz.exceptions import LLMProviderError
from qfzz.llm.client import MockLLMClient
from qfzz.llm.router import LLMRouter


def _fake_settings(**llm_overrides):
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = None
    settings.llm.together_api_key = None
    settings.llm.huggingface_api_key = None
    settings.llm.gemini_api_key = None
    for key, value in llm_overrides.items():
        setattr(settings.llm, key, value)
    return settings


def _router_with_unavailable_ollama(settings=None):
    settings = settings or _fake_settings()
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        return LLMRouter(config=settings)


class TestLLMRouterPackage:
    def test_falls_back_to_mock(self):
        router = _router_with_unavailable_ollama()
        names = [p["name"] for p in router.providers]
        assert "Mock" in names
        available = router.get_available_providers()
        assert "Mock" in available

    def test_generate_uses_available_provider(self):
        router = _router_with_unavailable_ollama()
        # Router may pass max_tokens; wrap mock provider to accept it
        for provider_info in router.providers:
            if provider_info["name"] == "Mock":
                provider_info["provider"].generate = (
                    lambda prompt, system_prompt=None, max_tokens=500: f"echo:{prompt}"
                )
        result = router.generate("hello")
        assert result["success"] is True
        assert result["provider"] == "Mock"
        assert "hello" in result["text"]

    def test_mock_client_always_listed(self):
        router = _router_with_unavailable_ollama()
        mock_providers = [
            p for p in router.providers if isinstance(p["provider"], MockLLMClient)
        ]
        assert len(mock_providers) == 1

    def test_skips_unhealthy_non_fallback_then_uses_mock(self):
        router = _router_with_unavailable_ollama()
        ollama_info = next(p for p in router.providers if p["name"] == "Ollama")
        ollama_info["provider"].is_available.return_value = False
        for provider_info in router.providers:
            if provider_info["name"] == "Mock":
                provider_info["provider"].generate = (
                    lambda prompt, system_prompt=None, max_tokens=500: f"echo:{prompt}"
                )
        result = router.generate("ping")
        assert result["success"] is True
        assert result["provider"] == "Mock"

    def test_failover_on_llm_provider_error(self):
        router = _router_with_unavailable_ollama()
        failing = MagicMock()
        failing.is_available.return_value = True
        failing.generate.side_effect = LLMProviderError("provider down")
        router.providers.insert(
            0, {"name": "FailingAPI", "provider": failing, "priority": 0, "type": "api"}
        )
        for provider_info in router.providers:
            if provider_info["name"] == "Mock":
                provider_info["provider"].generate = (
                    lambda prompt, system_prompt=None, max_tokens=500: f"echo:{prompt}"
                )
        result = router.generate("hello")
        assert result["success"] is True
        assert result["provider"] == "Mock"
        failing.generate.assert_called()

    def test_all_providers_fail_returns_error_payload(self):
        router = _router_with_unavailable_ollama()
        for provider_info in router.providers:
            provider = provider_info["provider"]
            if hasattr(provider, "is_available") and isinstance(
                getattr(provider, "is_available"), MagicMock
            ):
                provider.is_available.return_value = True
            provider.generate = MagicMock(side_effect=RuntimeError("boom"))
            # Force health check to treat real Mock as healthy via cache
            router._health_check_cache[provider_info["name"]] = {
                "healthy": True,
                "timestamp": 10**12,
            }
        result = router.generate("hello")
        assert result["success"] is False
        assert result["provider"] == "None"
        assert "error" in result

    def test_clear_health_cache_and_get_status(self):
        router = _router_with_unavailable_ollama()
        router._health_check_cache["Ollama"] = {"healthy": False, "timestamp": 0}
        router.clear_health_cache()
        assert router._health_check_cache == {}
        status = router.get_status()
        assert status["total_providers"] >= 1
        assert "Mock" in status["available_providers"]
        assert any(p["name"] == "Mock" for p in status["providers"])

    def test_initializes_groq_when_api_key_present(self):
        settings = _fake_settings(groq_api_key="test-groq-key")
        with (
            patch("qfzz.llm.router.get_config", return_value=settings),
            patch("qfzz.llm.router.OllamaClient") as ollama_cls,
            patch("qfzz.llm.router.GroqProvider") as groq_cls,
        ):
            ollama = MagicMock()
            ollama.is_available.return_value = False
            ollama_cls.return_value = ollama
            groq_cls.return_value = MagicMock()
            router = LLMRouter(config=settings)
            names = [p["name"] for p in router.providers]
            assert "Groq" in names
            groq_cls.assert_called_once_with(api_key="test-groq-key")
