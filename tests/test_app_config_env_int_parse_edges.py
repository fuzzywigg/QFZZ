"""App Config soft-fails non-integer env ints on reload."""

import importlib

import qfzz.app_config as app_config


def test_app_config_non_int_env_falls_back_to_defaults(monkeypatch):
    monkeypatch.setenv("QFZZ_PORT", "bad-port")
    monkeypatch.setenv("QFZZ_CACHE_EXPIRY_DAYS", "nope")
    monkeypatch.setenv("QFZZ_MAX_DOWNLOADS", "n/a")
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", "/tmp/qfzz-audio-int-parse")
    monkeypatch.setenv("QFZZ_CACHE_DIR", "/tmp/qfzz-cache-int-parse")

    importlib.reload(app_config)
    assert app_config.Config.PORT == 8080
    assert app_config.Config.CACHE_EXPIRY_DAYS == 30
    assert app_config.Config.MAX_DOWNLOADS == 3
