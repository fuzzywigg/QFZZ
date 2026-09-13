"""qfzz.llm.router constructor soft-fail per provider (Mock always remains)."""

from unittest.mock import MagicMock, patch

from qfzz.llm.router import LLMRouter


def _settings(**keys):
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = keys.get("groq")
    settings.llm.together_api_key = keys.get("together")
    settings.llm.huggingface_api_key = keys.get("hf")
    settings.llm.gemini_api_key = keys.get("gemini")
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


def test_together_hf_gemini_ctor_failures_soft_skip():
    settings = _settings(together="tog-test", hf="hf-test", gemini="gem-test")
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
        patch("qfzz.llm.router.TogetherProvider", side_effect=RuntimeError("tog fail")),
        patch("qfzz.llm.router.HuggingFaceProvider", side_effect=RuntimeError("hf fail")),
        patch("qfzz.llm.router.GeminiClient", side_effect=RuntimeError("gem fail")),
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        router = LLMRouter(config=settings)
        names = [p["name"] for p in router.providers]

    assert "Together.ai" not in names
    assert "HuggingFace" not in names
    assert "Gemini" not in names
    assert "Ollama" in names
    assert "Mock" in names
    priorities = [p["priority"] for p in router.providers]
    assert priorities == sorted(priorities)
