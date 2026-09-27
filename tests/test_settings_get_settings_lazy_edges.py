"""ConfigManager.get_settings reloads when _settings was cleared."""

from qfzz.config.settings import ConfigManager


def test_get_settings_reloads_when_settings_cleared(tmp_path):
    cfg = tmp_path / "qfzz.yaml"
    cfg.write_text("station:\n  name: LazyReload\n  port: 9090\n", encoding="utf-8")

    mgr = ConfigManager(config_file=str(cfg))
    assert mgr.get_settings().station.name == "LazyReload"

    mgr._settings = None
    settings = mgr.get_settings()
    assert settings is not None
    assert settings.station.name == "LazyReload"
    assert settings.station.port == 9090
