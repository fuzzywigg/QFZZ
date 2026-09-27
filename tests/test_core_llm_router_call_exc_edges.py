"""core.LLMRouter provider _call_* Exception → unsuccessful LLMResponse edges."""

from unittest.mock import patch

from qfzz.core.llm_router import LLMRouter


def test_call_groq_anthropic_openai_ollama_exception_paths(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)

    with patch("qfzz.core.llm_router.requests.post", side_effect=RuntimeError("groq down")):
        groq = router._call_groq("hi")
    assert groq.success is False
    assert groq.provider == "groq"
    assert "groq down" in (groq.error or "")

    with patch(
        "anthropic.Anthropic",
        side_effect=RuntimeError("anthropic down"),
    ):
        anth = router._call_anthropic("hi")
    assert anth.success is False
    assert anth.provider == "anthropic"
    assert "anthropic down" in (anth.error or "")

    with patch(
        "openai.OpenAI",
        side_effect=RuntimeError("openai down"),
    ):
        oai = router._call_openai("hi")
    assert oai.success is False
    assert oai.provider == "openai"
    assert "openai down" in (oai.error or "")

    with patch("qfzz.core.llm_router.requests.post", side_effect=RuntimeError("ollama down")):
        ola = router._call_ollama("hi")
    assert ola.success is False
    assert ola.provider == "ollama"
    assert "ollama down" in (ola.error or "")
