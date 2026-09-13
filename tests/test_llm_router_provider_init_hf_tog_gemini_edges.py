"""Package LLMRouter soft-skips HF / Together / Gemini ctor failures."""

from unittest.mock import MagicMock, patch

from qfzz.llm.router import LLMRouter


def _settings(groq=None, together=None, hf=None, gemini=None):
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = groq
    settings.llm.together_api_key = together
    settings.llm.huggingface_api_key = hf
    settings.llm.gemini_api_key = gemini
    return settings


def test_hf_together_gemini_ctor_failures_soft_skip_mock_remains():
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
        patch(
            "qfzz.llm.router.TogetherProvider",
            side_effect=RuntimeError("tog down"),
        ),
        patch(
            "qfzz.llm.router.HuggingFaceProvider",
            side_effect=ValueError("hf bad"),
        ),
        patch(
            "qfzz.llm.router.GeminiClient",
            side_effect=ImportError("no google"),
        ),
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        groq_cls.return_value = MagicMock()
        router = LLMRouter(config=settings)
        names = [p["name"] for p in router.providers]

    assert "Groq" in names
    assert "Together.ai" not in names
    assert "HuggingFace" not in names
    assert "Gemini" not in names
    assert "Mock" in names
