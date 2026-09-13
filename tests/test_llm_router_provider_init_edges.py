"""qfzz.llm.router provider init soft-fail and LLMProviderError continue edges."""

from unittest.mock import MagicMock, patch

from qfzz.exceptions import LLMProviderError
from qfzz.llm.router import LLMRouter


def _settings(
    groq=None,
    together=None,
    hf=None,
    gemini=None,
):
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = groq
    settings.llm.together_api_key = together
    settings.llm.huggingface_api_key = hf
    settings.llm.gemini_api_key = gemini
    return settings


def test_init_registers_providers_when_keys_set():
    settings = _settings(
        groq="gsk-test",
        together="tog-test",
        hf="hf-test",
        gemini="sk-test",
    )
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
        patch("qfzz.llm.router.GroqProvider") as groq_cls,
        patch("qfzz.llm.router.TogetherProvider") as tog_cls,
        patch("qfzz.llm.router.HuggingFaceProvider") as hf_cls,
        patch("qfzz.llm.router.GeminiClient") as gem_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        gem = MagicMock()
        gem.is_available.return_value = True
        gem_cls.return_value = gem

        router = LLMRouter(config=settings)
        names = [p["name"] for p in router.providers]

    assert names == [
        "Ollama",
        "Groq",
        "Together.ai",
        "HuggingFace",
        "Gemini",
        "Mock",
    ]
    groq_cls.assert_called_once_with(api_key="gsk-test")
    tog_cls.assert_called_once_with(api_key="tog-test")
    hf_cls.assert_called_once_with(api_key="hf-test")
    gem_cls.assert_called_once_with(api_key="sk-test")


def test_provider_constructor_failure_soft_skips():
    settings = _settings(groq="gsk-test", together="tog-test")
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
        patch("qfzz.llm.router.GroqProvider", side_effect=RuntimeError("bad key")),
        patch("qfzz.llm.router.TogetherProvider") as tog_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        tog_cls.return_value = MagicMock()
        router = LLMRouter(config=settings)
        names = [p["name"] for p in router.providers]

    assert "Groq" not in names
    assert "Together.ai" in names
    assert "Mock" in names


def test_generate_continues_on_llm_provider_error():
    settings = _settings()
    with (
        patch("qfzz.llm.router.get_config", return_value=settings),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = True
        ollama.generate.side_effect = LLMProviderError("ollama fail")
        ollama_cls.return_value = ollama
        router = LLMRouter(config=settings)
        # Ensure Mock succeeds
        for p in router.providers:
            if p["name"] == "Mock":
                p["provider"].generate = (
                    lambda prompt, system_prompt=None, max_tokens=500: "ok"
                )
        result = router.generate("hello")

    assert result["success"] is True
    assert result["provider"] == "Mock"
    assert result["text"] == "ok"
