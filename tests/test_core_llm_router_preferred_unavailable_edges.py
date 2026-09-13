"""core LLMRouter preferred-but-unavailable falls through to primary chain."""

from unittest.mock import patch

from qfzz.core.llm_router import LLMResponse, LLMRouter


def test_preferred_unavailable_uses_primary_fallback(temp_config, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk-test")
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    router = LLMRouter(config_path=temp_config)
    # preferred google unavailable → ignore preferred; use primary=groq
    router.config["providers"]["primary"] = "groq"
    router.providers["google"]["available"] = False
    router.providers["groq"]["available"] = True
    router.providers["ollama"]["available"] = False

    ok = LLMResponse(
        content="from-groq",
        provider="groq",
        model="m",
        cost=0.0,
        latency=0.01,
        success=True,
    )

    with (
        patch.object(router, "_call_google") as mock_google,
        patch.object(router, "_call_groq", return_value=ok) as mock_groq,
        patch.object(router, "_call_ollama") as mock_ollama,
    ):
        response = router.generate("hi", preferred_provider="google")

    assert response.success is True
    assert response.provider == "groq"
    mock_google.assert_not_called()
    mock_groq.assert_called_once()
    mock_ollama.assert_not_called()
