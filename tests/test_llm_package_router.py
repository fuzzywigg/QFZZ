"""Tests for qfzz.llm.router.LLMRouter provider selection."""

from unittest.mock import MagicMock, patch

from qfzz.llm.client import MockLLMClient
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


class TestLLMRouterPackage:
    def test_falls_back_to_mock(self):
        with (
            patch("qfzz.llm.router.get_config", return_value=_fake_settings()),
            patch("qfzz.llm.router.OllamaClient") as ollama_cls,
        ):
            ollama = MagicMock()
            ollama.is_available.return_value = False
            ollama_cls.return_value = ollama
            router = LLMRouter(config=_fake_settings())
            names = [p["name"] for p in router.providers]
            assert "Mock" in names
            available = router.get_available_providers()
            assert "Mock" in available

    def test_generate_uses_available_provider(self):
        with (
            patch("qfzz.llm.router.get_config", return_value=_fake_settings()),
            patch("qfzz.llm.router.OllamaClient") as ollama_cls,
        ):
            ollama = MagicMock()
            ollama.is_available.return_value = False
            ollama_cls.return_value = ollama
            router = LLMRouter(config=_fake_settings())
            # Router may pass max_tokens; wrap mock provider to accept it
            for provider_info in router.providers:
                if provider_info["name"] == "Mock":
                    provider_info["provider"].generate = (
                        lambda prompt, system_prompt=None, max_tokens=500: f"echo:{prompt}"
                    )
            result = router.generate("hello")
            assert result["success"] is True
            assert result["provider"] == "Mock"
            assert "hello" in result["text"]

    def test_mock_client_always_listed(self):
        with (
            patch("qfzz.llm.router.get_config", return_value=_fake_settings()),
            patch("qfzz.llm.router.OllamaClient") as ollama_cls,
        ):
            ollama = MagicMock()
            ollama.is_available.return_value = False
            ollama_cls.return_value = ollama
            router = LLMRouter(config=_fake_settings())
            mock_providers = [
                p for p in router.providers if isinstance(p["provider"], MockLLMClient)
            ]
            assert len(mock_providers) == 1
