"""ConfigManager keeps prior values when env ints are non-numeric."""

import yaml

from qfzz.config.settings import ConfigManager


def test_non_int_port_and_advanced_env_keep_yaml_defaults(tmp_path, monkeypatch):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        yaml.dump(
            {
                "station": {
                    "name": "Parse Station",
                    "port": 9090,
                    "audio_content_dir": str(tmp_path / "audio"),
                    "cache_dir": str(tmp_path / "cache"),
                },
                "logging": {"file": str(tmp_path / "logs" / "qfzz.log")},
                "advanced": {"cache_expiry_days": 14, "max_downloads": 4},
            }
        )
    )
    monkeypatch.setenv("QFZZ_PORT", "not-a-port")
    monkeypatch.setenv("QFZZ_CACHE_EXPIRY_DAYS", "abc")
    monkeypatch.setenv("QFZZ_MAX_DOWNLOADS", "xyz")

    settings = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings.station.port == 9090
    assert settings.advanced.cache_expiry_days == 14
    assert settings.advanced.max_downloads == 4


def test_empty_port_env_keeps_yaml_port(tmp_path, monkeypatch):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        yaml.dump(
            {
                "station": {
                    "port": 8123,
                    "audio_content_dir": str(tmp_path / "a"),
                    "cache_dir": str(tmp_path / "c"),
                },
                "logging": {"file": str(tmp_path / "l" / "x.log")},
            }
        )
    )
    monkeypatch.setenv("QFZZ_PORT", "")
    settings = ConfigManager(config_file=str(cfg_path)).get_settings()
    assert settings.station.port == 8123
