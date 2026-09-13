"""Harden app_config Config tests with importlib.reload for env-driven attrs."""

import importlib

import qfzz.app_config as app_config


class TestConfigReload:
    def test_reload_applies_env_overrides(self, monkeypatch):
        monkeypatch.setenv("QFZZ_STATION_NAME", "TESTSTATION")
        monkeypatch.setenv("QFZZ_PORT", "9099")
        monkeypatch.setenv("QFZZ_BLOCKCHAIN_ENABLED", "false")
        monkeypatch.setenv("QFZZ_EDGE_MODE", "true")
        monkeypatch.setenv("QFZZ_STRICT_LICENSING", "false")
        monkeypatch.setenv("LOG_LEVEL", "debug")
        monkeypatch.setenv("GOOGLE_AI_API_KEY", "reload-google")
        monkeypatch.setenv("GROQ_API_KEY", "reload-groq")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        importlib.reload(app_config)
        cfg = app_config.Config

        assert cfg.STATION_NAME == "TESTSTATION"
        assert cfg.PORT == 9099
        assert cfg.BLOCKCHAIN_ENABLED is False
        assert cfg.EDGE_MODE is True
        assert cfg.STRICT_LICENSING is False
        assert cfg.LOG_LEVEL == "DEBUG"
        assert cfg.is_configured() is True
        providers = cfg.get_configured_providers()
        assert "google" in providers
        assert "groq" in providers
        assert "ollama" in providers
        assert "anthropic" not in providers

    def test_reload_restores_defaults(self, monkeypatch):
        monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)
        monkeypatch.delenv("QFZZ_PORT", raising=False)
        monkeypatch.delenv("QFZZ_BLOCKCHAIN_ENABLED", raising=False)
        monkeypatch.delenv("QFZZ_EDGE_MODE", raising=False)
        monkeypatch.delenv("QFZZ_STRICT_LICENSING", raising=False)
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        importlib.reload(app_config)
        cfg = app_config.Config
        assert cfg.STATION_NAME == "QFZZ"
        assert cfg.PORT == 8080
        assert cfg.BLOCKCHAIN_ENABLED is True
        assert cfg.EDGE_MODE is False
        assert cfg.STRICT_LICENSING is True
        assert "ollama" in cfg.get_configured_providers()
