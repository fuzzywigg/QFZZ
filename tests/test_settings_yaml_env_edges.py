"""YAML/env edge coverage for ConfigManager (no secrets)."""

from pathlib import Path

import yaml

from qfzz.config.settings import ConfigManager


def test_corrupt_and_empty_yaml_use_defaults(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "audio"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "logs" / "x.log"))

    bad = tmp_path / "bad.yaml"
    bad.write_text(":\n  - not: valid: yaml: [[[")
    mgr = ConfigManager(config_file=str(bad))
    cfg = mgr.get_settings()
    assert cfg.station.name  # defaults applied

    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    mgr2 = ConfigManager(config_file=str(empty))
    assert mgr2.get_settings().station.port > 0


def test_unknown_yaml_keys_ignored(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))
    path = tmp_path / "cfg.yaml"
    path.write_text(
        yaml.dump(
            {
                "station": {
                    "name": "Edge Station",
                    "audio_content_dir": str(tmp_path / "a"),
                    "cache_dir": str(tmp_path / "c"),
                },
                "logging": {"file": str(tmp_path / "l" / "x.log")},
                "totally_unknown_section": {"x": 1},
            }
        )
    )
    mgr = ConfigManager(config_file=str(path))
    assert mgr.get_settings().station.name == "Edge Station"


def test_env_bool_case_sensitivity(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("QFZZ_AUDIO_CONTENT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("QFZZ_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("QFZZ_LOG_FILE", str(tmp_path / "l" / "x.log"))
    path = tmp_path / "cfg.yaml"
    path.write_text(
        yaml.dump(
            {
                "station": {
                    "name": "B",
                    "audio_content_dir": str(tmp_path / "a"),
                    "cache_dir": str(tmp_path / "c"),
                },
                "logging": {"file": str(tmp_path / "l" / "x.log")},
            }
        )
    )
    # Implementation uses .lower() == "true"
    monkeypatch.setenv("QFZZ_EDGE_MODE", "TRUE")
    monkeypatch.setenv("QFZZ_ENABLE_6G", "1")
    mgr = ConfigManager(config_file=str(path))
    cfg = mgr.get_settings()
    assert cfg.station.edge_mode is True
    assert cfg.station.enable_6g is False  # "1" is not "true"

    monkeypatch.setenv("QFZZ_ENABLE_6G", "true")
    mgr2 = ConfigManager(config_file=str(path))
    assert mgr2.get_settings().station.enable_6g is True
