"""HealthChecker.check_disk_space inclusive free-space boundary (>=)."""

from unittest.mock import MagicMock, patch

from qfzz.utils.health import HealthChecker


def test_disk_space_exact_min_is_healthy_below_is_degraded():
    checker = HealthChecker()
    usage = MagicMock()
    usage.free = int(1.0 * (1024**3))  # exactly 1.0 GiB
    usage.total = int(10 * (1024**3))

    with patch("qfzz.utils.health.psutil.disk_usage", return_value=usage):
        ok = checker.check_disk_space(path=".", min_free_gb=1.0)
    assert ok["status"] == "healthy"
    assert abs(ok["free_gb"] - 1.0) < 1e-9

    usage.free = int(0.999 * (1024**3))
    with patch("qfzz.utils.health.psutil.disk_usage", return_value=usage):
        bad = checker.check_disk_space(path=".", min_free_gb=1.0)
    assert bad["status"] == "degraded"
