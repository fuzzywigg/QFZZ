"""YAML section / env / port validation edges for ConfigManager (dummy values only)."""

from pathlib import Path

import yaml

from qfzz.config.settings import (
    AdvancedSettings,
    ConfigManager,
    LLMSettings,
    MusicSourceSettings,
)


def test_yaml_llm_music_logging_advanced_sections(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        yaml.dump(
            {
                "station": {
                    "name": "Section Station",
                    "port": 9090,
                    "audio_content_dir": str(tmp_path / "audio"),
                    "cache_dir": str(tmp_path / "cache"),
                },
                "llm": {
                    "ollama_base_url": "http://127.0.0.1:11434",
                    "ollama_model": "tinyllama",
                    "unknown_llm_key": "ignored",
                },
                "music_sources": {"jamendo_client_id": "jam-test"},
                "logging": {
                    "level": "DEBUG",
                    "file": str(tmp_path / "logs" / "qfzz.log"),
                },
                "advanced": {
                    "strict_licensing": False,
                    "cache_expiry_days": 7,
                    "max_downloads": 2,
                },
                "totally_unknown": {"x": 1},
            }
        )
    )
    monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)
    monkeypatch.delenv("QFZZ_PORT", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("QFZZ_LOG_LEVEL", raising=False)
    # Env overrides YAML for these keys — pin them so section apply stays visible.
    monkeypatch.setenv("QFZZ_STRICT_LICENSING", "false")
    monkeypatch.setenv("QFZZ_CACHE_EXPIRY_DAYS", "7")
    monkeypatch.setenv("QFZZ_MAX_DOWNLOADS", "2")
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "audio"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "logs" / "qfzz.log"))

    settings = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings.station.name == "Section Station"
    assert settings.station.port == 9090
    assert settings.llm.ollama_model == "tinyllama"
    assert settings.llm.ollama_base_url == "http://127.0.0.1:11434"
    assert settings.music_sources.jamendo_client_id == "jam-test"
    assert settings.logging.level == "DEBUG"
    assert settings.advanced.strict_licensing is False
    assert settings.advanced.cache_expiry_days == 7
    assert settings.advanced.max_downloads == 2


def test_corrupt_yaml_soft_fails_to_defaults(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "bad.yaml"
    cfg_path.write_text(":\n  - !!python/object/apply:os.system ['echo no']\n", encoding="utf-8")
    # Actually use simply invalid YAML that safe_load may fail on
    cfg_path.write_text("[\n  unclosed", encoding="utf-8")
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))
    monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)

    settings = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings.station.name == "QFZZ"
    assert settings.station.port == 8080


def test_find_config_file_discovers_config_default_yaml(tmp_path: Path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yaml").write_text(
        yaml.dump(
            {
                "station": {
                    "name": "Discovered",
                    "audio_content_dir": str(tmp_path / "a"),
                    "cache_dir": str(tmp_path / "c"),
                },
                "logging": {"file": str(tmp_path / "l" / "x.log")},
            }
        )
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))

    mgr = ConfigManager()
    assert mgr.config_file is not None
    assert mgr.config_file.endswith("config/default.yaml")
    assert mgr.get_settings().station.name == "Discovered"


def test_env_advanced_and_port_boundaries(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "empty.yaml"
    cfg_path.write_text("", encoding="utf-8")
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))
    monkeypatch.setenv("QFZZ_CACHE_EXPIRY_DAYS", "14")
    monkeypatch.setenv("QFZZ_MAX_DOWNLOADS", "9")
    monkeypatch.setenv("QFZZ_STRICT_LICENSING", "false")
    monkeypatch.setenv("QFZZ_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("QFZZ_PORT", "1023")
    monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)

    settings = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings.advanced.cache_expiry_days == 14
    assert settings.advanced.max_downloads == 9
    assert settings.advanced.strict_licensing is False
    assert settings.logging.level == "WARNING"
    assert settings.station.port == 8080  # clamped

    monkeypatch.setenv("QFZZ_PORT", "1024")
    settings2 = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings2.station.port == 1024

    monkeypatch.setenv("QFZZ_PORT", "65535")
    settings3 = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings3.station.port == 65535


def test_dataclass_defaults_without_secrets():
    llm = LLMSettings()
    assert llm.gemini_api_key is None
    assert llm.groq_api_key is None
    music = MusicSourceSettings()
    assert music.jamendo_client_id is None
    adv = AdvancedSettings()
    assert adv.strict_licensing is True
    assert adv.cache_expiry_days == 30
