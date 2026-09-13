"""Health-cache / fail-all / status edges for package LLMRouter."""

import time
from unittest.mock import MagicMock, patch

from qfzz.llm.router import LLMRouter


def _fake_settings():
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = None
    settings.llm.together_api_key = None
    settings.llm.huggingface_api_key = None
    settings.llm.gemini_api_key = None
    return settings


def _router_with_providers(providers):
    with (
        patch("qfzz.llm.router.get_config", return_value=_fake_settings()),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        router = LLMRouter(config=_fake_settings())
    router.providers = providers
    router._health_check_cache.clear()
    return router


def test_unhealthy_non_fallback_skipped_uses_mock():
    unhealthy = MagicMock()
    unhealthy.is_available.return_value = False
    unhealthy.generate.side_effect = AssertionError("should not be called")

    mock = MagicMock()
    mock.is_available.return_value = True
    mock.generate.return_value = "ok"

    router = _router_with_providers(
        [
            {"name": "Broken", "provider": unhealthy, "priority": 1, "type": "api"},
            {"name": "Mock", "provider": mock, "priority": 99, "type": "fallback"},
        ]
    )
    result = router.generate("hi")
    assert result["success"] is True
    assert result["provider"] == "Mock"
    unhealthy.generate.assert_not_called()


def test_is_available_exception_cached_false_then_clear():
    flaky = MagicMock()
    flaky.is_available.side_effect = RuntimeError("down")
    mock = MagicMock()
    mock.is_available.return_value = True
    mock.generate.return_value = "fallback"

    router = _router_with_providers(
        [
            {"name": "Flaky", "provider": flaky, "priority": 1, "type": "api"},
            {"name": "Mock", "provider": mock, "priority": 99, "type": "fallback"},
        ]
    )
    assert router._is_provider_healthy(router.providers[0]) is False
    # Cached — should not call is_available again
    flaky.is_available.side_effect = None
    flaky.is_available.return_value = True
    assert router._is_provider_healthy(router.providers[0]) is False

    router.clear_health_cache()
    assert router._is_provider_healthy(router.providers[0]) is True


def test_health_cache_ttl_expiry():
    provider = MagicMock()
    provider.is_available.return_value = True
    router = _router_with_providers(
        [{"name": "P", "provider": provider, "priority": 1, "type": "api"}]
    )
    router._health_check_ttl = 0.01
    assert router._is_provider_healthy(router.providers[0]) is True
    provider.is_available.return_value = False
    time.sleep(0.02)
    assert router._is_provider_healthy(router.providers[0]) is False


def test_get_status_and_all_providers_fail():
    bad = MagicMock()
    bad.is_available.return_value = True
    bad.generate.side_effect = RuntimeError("fail")

    router = _router_with_providers(
        [{"name": "Only", "provider": bad, "priority": 1, "type": "api"}]
    )
    status = router.get_status()
    assert status["total_providers"] == 1
    assert "Only" in status["available_providers"]

    result = router.generate("x")
    assert result["success"] is False
    assert result["provider"] == "None"
    assert "unavailable" in result["text"].lower() or "failed" in result["text"].lower()
