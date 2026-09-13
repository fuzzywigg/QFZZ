"""Tests for ConfigManager YAML + env overrides."""

from pathlib import Path

import yaml

from qfzz.config.settings import ConfigManager, StationSettings


class TestConfigManager:
    def test_yaml_and_env_overrides(self, tmp_path, monkeypatch):
        cfg_path = tmp_path / "config.yaml"
        cfg_path.write_text(
            yaml.dump(
                {
                    "station": {
                        "name": "YAML Station",
                        "port": 9090,
                        "audio_content_dir": str(tmp_path / "audio"),
                        "cache_dir": str(tmp_path / "cache"),
                    },
                    "logging": {"level": "DEBUG", "file": str(tmp_path / "logs" / "qfzz.log")},
                    "advanced": {"max_downloads": 7},
                }
            )
        )
        monkeypatch.setenv("QFZZ_STATION_NAME", "Env Station")
        monkeypatch.setenv("QFZZ_PORT", "8123")
        monkeypatch.setenv("QFZZ_EDGE_MODE", "true")
        monkeypatch.setenv("OLLAMA_MODEL", "mistral")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        mgr = ConfigManager(config_file=str(cfg_path))
        settings = mgr.get_settings()
        assert settings.station.name == "Env Station"
        assert settings.station.port == 8123
        assert settings.station.edge_mode is True
        assert settings.llm.ollama_model == "mistral"
        assert settings.advanced.max_downloads == 7
        assert Path(settings.station.audio_content_dir).exists()
        assert Path(settings.station.cache_dir).exists()

    def test_invalid_port_falls_back(self, tmp_path, monkeypatch):
        cfg_path = tmp_path / "config.yaml"
        cfg_path.write_text(
            yaml.dump(
                {
                    "station": {
                        "port": 80,
                        "audio_content_dir": str(tmp_path / "a"),
                        "cache_dir": str(tmp_path / "c"),
                    },
                    "logging": {"file": str(tmp_path / "l" / "x.log")},
                }
            )
        )
        monkeypatch.delenv("QFZZ_PORT", raising=False)
        settings = ConfigManager(config_file=str(cfg_path)).get_settings()
        assert settings.station.port == 8080

    def test_defaults_without_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        for key in (
            "QFZZ_STATION_NAME",
            "QFZZ_PORT",
            "QFZZ_EDGE_MODE",
            "QFZZ_AUDIO_CONTENT_DIR",
            "QFZZ_CACHE_DIR",
            "QFZZ_LOG_FILE",
        ):
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "audio"))
        monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "cache"))
        monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "logs" / "qfzz.log"))
        settings = ConfigManager(config_file=str(tmp_path / "missing.yaml")).get_settings()
        assert isinstance(settings.station, StationSettings)
        assert settings.station.name == "QFZZ"

    def test_reload(self, tmp_path, monkeypatch):
        cfg_path = tmp_path / "config.yaml"
        cfg_path.write_text(
            yaml.dump(
                {
                    "station": {
                        "name": "One",
                        "audio_content_dir": str(tmp_path / "a"),
                        "cache_dir": str(tmp_path / "c"),
                    },
                    "logging": {"file": str(tmp_path / "l" / "x.log")},
                }
            )
        )
        monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)
        mgr = ConfigManager(config_file=str(cfg_path))
        assert mgr.get_settings().station.name == "One"
        cfg_path.write_text(
            yaml.dump(
                {
                    "station": {
                        "name": "Two",
                        "audio_content_dir": str(tmp_path / "a"),
                        "cache_dir": str(tmp_path / "c"),
                    },
                    "logging": {"file": str(tmp_path / "l" / "x.log")},
                }
            )
        )
        mgr.reload()
        assert mgr.get_settings().station.name == "Two"
