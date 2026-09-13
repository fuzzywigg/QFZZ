"""HealthChecker exact threshold equality edges."""

from unittest.mock import MagicMock, patch

from qfzz.utils.health import HealthChecker


def test_memory_exact_max_percent_is_degraded():
    checker = HealthChecker()
    mem = MagicMock(percent=90.0, available=100 * (1024**2), total=1000 * (1024**2))
    with patch("qfzz.utils.health.psutil.virtual_memory", return_value=mem):
        assert checker.check_memory(max_percent=90.0)["status"] == "degraded"


def test_cpu_exact_max_percent_is_degraded():
    checker = HealthChecker()
    with (
        patch("qfzz.utils.health.psutil.cpu_percent", return_value=90.0),
        patch("qfzz.utils.health.psutil.cpu_count", return_value=4),
    ):
        assert checker.check_cpu(max_percent=90.0)["status"] == "degraded"


def test_disk_exact_min_free_gb_is_healthy():
    checker = HealthChecker()
    usage = MagicMock(free=1.0 * (1024**3), total=10 * (1024**3), percent=90.0)
    with patch("qfzz.utils.health.psutil.disk_usage", return_value=usage):
        result = checker.check_disk_space(min_free_gb=1.0)
    assert result["status"] == "healthy"
    assert result["free_gb"] == 1.0
