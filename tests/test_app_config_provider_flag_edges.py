"""App Config provider list / LOG_LEVEL / edge+6g flag edges via reload."""

import importlib

import qfzz.app_config as app_config


def test_configured_providers_order_and_flags(monkeypatch):
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "sk-test-google")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-test")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("QFZZ_EDGE_MODE", "TRUE")
    monkeypatch.setenv("QFZZ_ENABLE_6G", "True")
    monkeypatch.setenv("GOOGLE_AI_MODEL_DEFAULT", "gemini-flash-test")

    importlib.reload(app_config)

    assert app_config.Config.get_configured_providers() == [
        "google",
        "groq",
        "ollama",
    ]
    assert app_config.Config.LOG_LEVEL == "DEBUG"
    assert app_config.Config.EDGE_MODE is True
    assert app_config.Config.ENABLE_6G is True
    assert app_config.Config.GOOGLE_AI_MODEL_DEFAULT == "gemini-flash-test"

    # Restore defaults for other suites that reload this module
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("QFZZ_EDGE_MODE", raising=False)
    monkeypatch.delenv("QFZZ_ENABLE_6G", raising=False)
    monkeypatch.delenv("GOOGLE_AI_MODEL_DEFAULT", raising=False)
    importlib.reload(app_config)
