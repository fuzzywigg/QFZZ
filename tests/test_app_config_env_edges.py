"""App Config env flag edges via importlib.reload (dummy values only)."""

import importlib

import qfzz.app_config as app_config


def test_app_config_audit_cache_downloads_flags(monkeypatch):
    monkeypatch.setenv("ENABLE_AUDIT_LOGGING", "false")
    monkeypatch.setenv("QFZZ_CACHE_EXPIRY_DAYS", "11")
    monkeypatch.setenv("QFZZ_MAX_DOWNLOADS", "5")
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", "/tmp/qfzz-audio-test")
    monkeypatch.setenv("QFZZ_CACHE_DIR", "/tmp/qfzz-cache-test")
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    importlib.reload(app_config)
    assert app_config.Config.ENABLE_AUDIT_LOGGING is False
    assert app_config.Config.CACHE_EXPIRY_DAYS == 11
    assert app_config.Config.MAX_DOWNLOADS == 5
    assert str(app_config.Config.AUDIO_CONTENT_DIR).endswith("qfzz-audio-test")
    assert str(app_config.Config.CACHE_DIR).endswith("qfzz-cache-test")
    # Ollama always counted → always configured
    assert app_config.Config.is_configured() is True
