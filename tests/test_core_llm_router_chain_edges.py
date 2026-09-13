"""qfzz.core.llm_router generate-chain and stats edges (mocked providers only)."""

from unittest.mock import patch

from qfzz.core.llm_router import LLMResponse, LLMRouter


def test_preferred_unavailable_falls_back_to_primary(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    router.providers["google"]["available"] = False

    with patch.object(router, "_call_groq") as mock_groq:
        mock_groq.return_value = LLMResponse(
            content="via-groq",
            provider="groq",
            model="llama",
            cost=0.0,
            latency=0.1,
            success=True,
        )
        response = router.generate("hi", preferred_provider="google")

    assert response.success is True
    assert response.provider == "groq"
    mock_groq.assert_called_once()


def test_unknown_provider_in_chain_is_skipped(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    router.config["providers"]["primary"] = "not-a-real-provider"
    router.config["providers"]["fallback_chain"] = ["groq"]
    for name in router.providers:
        router.providers[name]["available"] = name == "groq"

    with patch.object(router, "_call_groq") as mock_groq:
        mock_groq.return_value = LLMResponse(
            content="ok",
            provider="groq",
            model="llama",
            cost=0.0,
            latency=0.1,
            success=True,
        )
        response = router.generate("ping")

    assert response.success is True
    assert response.provider == "groq"


def test_provider_exception_continues_to_next(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    for name in router.providers:
        router.providers[name]["available"] = name in {"google", "groq"}

    with (
        patch.object(router, "_call_google", side_effect=RuntimeError("boom")),
        patch.object(router, "_call_groq") as mock_groq,
    ):
        mock_groq.return_value = LLMResponse(
            content="recovered",
            provider="groq",
            model="llama",
            cost=0.0,
            latency=0.1,
            success=True,
        )
        response = router.generate("x")

    assert response.success is True
    assert response.content == "recovered"


def test_get_stats_zero_requests_average_cost_is_zero(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    stats = router.get_stats()
    assert stats["total_requests"] == 0
    assert stats["average_cost"] == 0
    assert stats["total_cost"] == 0.0
