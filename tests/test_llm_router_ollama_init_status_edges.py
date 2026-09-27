"""llm.router Ollama init failure and unavailable_providers status edges."""

from unittest.mock import MagicMock, patch

from qfzz.llm.router import LLMRouter


def test_ollama_init_exception_skips_provider():
    cfg = MagicMock()
    cfg.llm.ollama_model = "llama3"
    cfg.llm.ollama_base_url = "http://localhost:11434"
    cfg.llm.groq_api_key = None
    cfg.llm.together_api_key = None
    cfg.llm.huggingface_api_key = None
    cfg.llm.gemini_api_key = None

    with patch("qfzz.llm.router.OllamaClient", side_effect=RuntimeError("ctor fail")):
        router = LLMRouter(config=cfg)

    names = [p["name"] for p in router.providers]
    assert "Ollama" not in names
    assert "Mock" in names


def test_get_status_lists_unavailable_providers():
    cfg = MagicMock()
    cfg.llm.ollama_model = "llama3"
    cfg.llm.ollama_base_url = "http://localhost:9"
    cfg.llm.groq_api_key = None
    cfg.llm.together_api_key = None
    cfg.llm.huggingface_api_key = None
    cfg.llm.gemini_api_key = None

    unhealthy = MagicMock()
    unhealthy.is_available.return_value = False
    mock = MagicMock()
    mock.is_available.return_value = True

    with (
        patch("qfzz.llm.router.OllamaClient", return_value=unhealthy),
        patch("qfzz.llm.router.MockLLMClient", return_value=mock),
    ):
        router = LLMRouter(config=cfg)
        # Force health cache miss / direct unhealthy for Ollama entry
        for p in router.providers:
            if p["name"] == "Ollama":
                p["provider"] = unhealthy
                p["type"] = "local"

        status = router.get_status()

    assert "Ollama" in status["unavailable_providers"] or any(
        not s["healthy"] for s in status["providers"] if s["name"] == "Ollama"
    )
