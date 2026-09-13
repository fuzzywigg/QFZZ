"""HealthChecker version file / threshold / missing-file edges."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from qfzz.utils.health import HealthChecker, HealthStatus


def test_get_version_reads_version_file(tmp_path, monkeypatch):
    version_file = tmp_path / "VERSION"
    version_file.write_text("9.9.9\n", encoding="utf-8")
    # HealthChecker looks at Path(__file__).parent.parent / "VERSION"
    # which is qfzz/VERSION — patch Path.read_text on that resolution via monkeypatch
    checker = HealthChecker()
    with patch.object(Path, "exists", return_value=True), patch.object(
        Path, "read_text", return_value="2.3.4\n"
    ):
        assert checker._get_version() == "2.3.4"


def test_get_version_falls_back_on_oserror():
    checker = HealthChecker()
    with patch.object(Path, "exists", side_effect=OSError("boom")):
        assert checker._get_version() == "1.0.0"


def test_disk_degraded_when_below_threshold():
    checker = HealthChecker()
    usage = MagicMock(free=0.5 * (1024**3), total=10 * (1024**3), percent=95.0)
    with patch("qfzz.utils.health.psutil.disk_usage", return_value=usage):
        result = checker.check_disk_space(min_free_gb=1.0)
    assert result["status"] == "degraded"
    assert result["free_gb"] == 0.5


def test_memory_and_cpu_degraded_thresholds():
    checker = HealthChecker()
    mem = MagicMock(percent=95.0, available=100 * (1024**2), total=1000 * (1024**2))
    with patch("qfzz.utils.health.psutil.virtual_memory", return_value=mem):
        assert checker.check_memory(max_percent=90.0)["status"] == "degraded"
    with (
        patch("qfzz.utils.health.psutil.cpu_percent", return_value=99.0),
        patch("qfzz.utils.health.psutil.cpu_count", return_value=4),
    ):
        assert checker.check_cpu(max_percent=90.0)["status"] == "degraded"


def test_check_file_exists_missing_and_oserror(tmp_path):
    checker = HealthChecker()
    missing = checker.check_file_exists(str(tmp_path / "nope.txt"), "cfg")
    assert missing["status"] == "degraded"
    assert missing["exists"] is False

    with patch("qfzz.utils.health.Path.exists", side_effect=OSError("stat fail")):
        bad = checker.check_file_exists("/x", "cfg")
    assert bad["status"] == "unhealthy"


def test_to_json_roundtrip():
    checker = HealthChecker()
    status = HealthStatus(
        status="healthy",
        timestamp="2026-01-01T00:00:00",
        uptime_seconds=1.5,
        version="1.0.0",
        checks={"disk": {"status": "healthy"}},
    )
    payload = checker.to_json(status)
    assert '"status": "healthy"' in payload
    assert "disk" in payload
