"""Tests for HealthChecker utilities."""

from unittest.mock import patch

from qfzz.utils.health import HealthChecker, HealthStatus, health_check


def test_health_checker_version_nonempty():
    checker = HealthChecker()
    assert isinstance(checker.version, str)
    assert len(checker.version) > 0


def test_check_disk_and_memory_healthy():
    checker = HealthChecker()
    disk = checker.check_disk_space(path=".", min_free_gb=0.0)
    assert disk["status"] in {"healthy", "degraded"}
    assert "free_gb" in disk

    memory = checker.check_memory(max_percent=100.0)
    assert memory["status"] == "healthy"
    assert "percent_used" in memory


def test_check_all_returns_health_status():
    checker = HealthChecker()
    with (
        patch.object(checker, "check_disk_space", return_value={"status": "healthy"}),
        patch.object(checker, "check_memory", return_value={"status": "healthy"}),
        patch.object(checker, "check_cpu", return_value={"status": "healthy"}),
        patch.object(checker, "check_ledger_integrity", return_value={"status": "healthy"}),
        patch.object(checker, "check_file_exists", return_value={"status": "healthy"}),
    ):
        status = checker.check_all()
        assert isinstance(status, HealthStatus)
        assert status.status == "healthy"
        assert "disk_space" in status.checks
        payload = checker.to_dict(status)
        assert payload["status"] == "healthy"


def test_check_all_unhealthy_when_any_check_fails():
    checker = HealthChecker()
    with (
        patch.object(checker, "check_disk_space", return_value={"status": "healthy"}),
        patch.object(checker, "check_memory", return_value={"status": "unhealthy"}),
        patch.object(checker, "check_cpu", return_value={"status": "healthy"}),
        patch.object(checker, "check_ledger_integrity", return_value={"status": "healthy"}),
        patch.object(checker, "check_file_exists", return_value={"status": "healthy"}),
    ):
        status = checker.check_all()
        assert status.status == "unhealthy"


def test_check_disk_space_error_path():
    checker = HealthChecker()
    with patch("qfzz.utils.health.psutil.disk_usage", side_effect=OSError("boom")):
        result = checker.check_disk_space()
        assert result["status"] == "unhealthy"
        assert "error" in result


def test_health_check_convenience():
    with patch.object(HealthChecker, "check_all", return_value=HealthStatus(
        status="healthy",
        timestamp="t",
        uptime_seconds=1.0,
        version="0.1.0",
        checks={},
    )):
        status = health_check()
        assert status.status == "healthy"
