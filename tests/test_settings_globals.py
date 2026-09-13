"""Global get_config / reload_config and YAML edge paths (no secrets)."""

from pathlib import Path

import yaml

import qfzz.config.settings as settings_mod
from qfzz.config.settings import ConfigManager, get_config, reload_config


def test_get_config_and_reload_globals(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        yaml.dump(
            {
                "station": {
                    "name": "Global One",
                    "port": 8120,
                    "audio_content_dir": str(tmp_path / "a"),
                    "cache_dir": str(tmp_path / "c"),
                },
                "logging": {"file": str(tmp_path / "l" / "x.log")},
            }
        )
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)
    monkeypatch.delenv("QFZZ_PORT", raising=False)
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))

    settings_mod._config_manager = None
    # Force ConfigManager default path by patching after construction via direct assign
    settings_mod._config_manager = ConfigManager(config_file=str(cfg_path))
    cfg = get_config()
    assert cfg.station.name == "Global One"

    cfg_path.write_text(
        yaml.dump(
            {
                "station": {
                    "name": "Global Two",
                    "audio_content_dir": str(tmp_path / "a"),
                    "cache_dir": str(tmp_path / "c"),
                },
                "logging": {"file": str(tmp_path / "l" / "x.log")},
            }
        )
    )
    reload_config()
    assert get_config().station.name == "Global Two"

    settings_mod._config_manager = None
    reload_config()
    assert settings_mod._config_manager is not None


def test_yaml_non_mapping_and_bool_env(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("just-a-string\n", encoding="utf-8")
    monkeypatch.setenv("QFZZ_EDGE_MODE", "false")
    monkeypatch.setenv("QFZZ_BLOCKCHAIN_ENABLED", "false")
    monkeypatch.setenv("QFZZ_PORT", "65536")
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))
    monkeypatch.delenv("QFZZ_STATION_NAME", raising=False)

    settings = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings.station.edge_mode is False
    assert settings.station.blockchain_enabled is False
    assert settings.station.port == 8080

    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    settings2 = ConfigManager(config_file=str(empty)).get_settings()
    assert settings2.station.name  # defaults still load
