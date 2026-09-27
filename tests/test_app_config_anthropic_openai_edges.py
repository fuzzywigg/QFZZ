"""App Config lists anthropic/openai when those API keys are present."""

import importlib

import qfzz.app_config as app_config


def test_configured_providers_includes_anthropic_and_openai(monkeypatch):
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test")

    importlib.reload(app_config)

    providers = app_config.Config.get_configured_providers()
    assert providers == ["anthropic", "openai", "ollama"]

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    importlib.reload(app_config)
