"""qfzz.core.llm_router per-provider _call_* failure edges (mocked HTTP/SDKs)."""

from unittest.mock import MagicMock, patch

from qfzz.core.llm_router import LLMRouter


def test_call_groq_http_exception_returns_failure(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    with patch("qfzz.core.llm_router.requests.post", side_effect=RuntimeError("groq down")):
        response = router._call_groq("ping")
    assert response.success is False
    assert response.provider == "groq"
    assert response.content == ""
    assert "groq down" in (response.error or "")


def test_call_ollama_raise_for_status_failure(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = RuntimeError("ollama 500")
    with patch("qfzz.core.llm_router.requests.post", return_value=mock_resp):
        response = router._call_ollama("ping")
    assert response.success is False
    assert response.provider == "ollama"
    assert "ollama 500" in (response.error or "")


def test_call_anthropic_ctor_failure(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    fake_anthropic = MagicMock()
    fake_anthropic.Anthropic.side_effect = RuntimeError("anthropic auth")
    with patch.dict("sys.modules", {"anthropic": fake_anthropic}):
        response = router._call_anthropic("ping")
    assert response.success is False
    assert response.provider == "anthropic"
    assert "anthropic auth" in (response.error or "")


def test_call_openai_api_failure(mock_env, temp_config):
    router = LLMRouter(config_path=temp_config)
    client = MagicMock()
    client.chat.completions.create.side_effect = RuntimeError("openai boom")
    fake_openai = MagicMock()
    fake_openai.OpenAI.return_value = client
    with patch.dict("sys.modules", {"openai": fake_openai}):
        response = router._call_openai("ping")
    assert response.success is False
    assert response.provider == "openai"
    assert "openai boom" in (response.error or "")
