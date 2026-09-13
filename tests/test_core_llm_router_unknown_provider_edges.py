"""core LLMRouter unknown primary provider skip / all-fail edges."""

from unittest.mock import patch

from qfzz.core.llm_router import LLMResponse, LLMRouter


def test_unknown_primary_skipped_falls_through_to_available(temp_config, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk-test")
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    router = LLMRouter(config_path=temp_config)
    router.config["providers"]["primary"] = "ghost"
    router.config["providers"]["fallback_chain"] = ["ghost", "groq", "ollama"]
    router.providers["groq"]["available"] = True
    router.providers["ollama"]["available"] = False
    for name in ("google", "anthropic", "openai"):
        router.providers[name]["available"] = False

    ok = LLMResponse(
        content="from-groq",
        provider="groq",
        model="m",
        cost=0.0,
        latency=0.01,
        success=True,
    )

    with (
        patch.object(router, "_call_groq", return_value=ok) as mock_groq,
        patch.object(router, "_call_ollama") as mock_ollama,
    ):
        response = router.generate("hi")

    assert response.success is True
    assert response.provider == "groq"
    mock_groq.assert_called_once()
    mock_ollama.assert_not_called()


def test_all_unknown_providers_fail(temp_config, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    router = LLMRouter(config_path=temp_config)
    router.config["providers"]["primary"] = "phantom"
    router.config["providers"]["fallback_chain"] = ["spectre"]
    for name in router.providers:
        router.providers[name]["available"] = False

    response = router.generate("hi")
    assert response.success is False
    assert response.provider == "none"
    assert "All providers failed" in (response.error or "")
