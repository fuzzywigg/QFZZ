"""Icecast update_metadata defaults and package router generic Exception continue."""

import sys
from unittest.mock import MagicMock, Mock, patch

sys.modules.setdefault("shout", MagicMock())

from qfzz.llm.router import LLMRouter  # noqa: E402
from qfzz.streaming.icecast_client import (  # noqa: E402
    IcecastClient,
    IcecastConfig,
    IcecastState,
)


def test_update_metadata_empty_track_uses_unknown_defaults():
    import shout as mock_shout

    mock_instance = Mock()
    mock_metadata = Mock()
    mock_shout.Metadata.return_value = mock_metadata

    with patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True):
        client = IcecastClient(IcecastConfig())
        client._state = IcecastState.CONNECTED
        client._shout = mock_instance
        assert client.update_metadata({}) is True

    mock_metadata.add.assert_called_once_with("song", "Unknown Artist - Unknown Title")
    mock_instance.set_metadata.assert_called_once_with(mock_metadata)


def _fake_settings():
    settings = MagicMock()
    settings.llm.ollama_model = "llama3"
    settings.llm.ollama_base_url = "http://localhost:9"
    settings.llm.groq_api_key = None
    settings.llm.together_api_key = None
    settings.llm.huggingface_api_key = None
    settings.llm.gemini_api_key = None
    return settings


def test_package_router_generic_exception_continues_to_next_provider():
    with (
        patch("qfzz.llm.router.get_config", return_value=_fake_settings()),
        patch("qfzz.llm.router.OllamaClient") as ollama_cls,
    ):
        ollama = MagicMock()
        ollama.is_available.return_value = False
        ollama_cls.return_value = ollama
        router = LLMRouter(config=_fake_settings())

        boom = MagicMock()
        boom.generate.side_effect = RuntimeError("provider exploded")
        ok = MagicMock()
        ok.generate.side_effect = lambda prompt, system_prompt=None, max_tokens=500: f"echo:{prompt}"

        router.providers = [
            {"name": "Boom", "type": "primary", "provider": boom},
            {"name": "Rescue", "type": "fallback", "provider": ok},
        ]
        with patch.object(router, "_is_provider_healthy", return_value=True):
            result = router.generate("hello")

        assert result["success"] is True
        assert result["provider"] == "Rescue"
        assert "hello" in result["text"]
