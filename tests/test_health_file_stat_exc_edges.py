"""HealthChecker check_file_exists when Path.stat raises after exists."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from qfzz.utils.health import HealthChecker


def test_check_file_exists_stat_exception_is_unhealthy(tmp_path: Path):
    target = tmp_path / "present.txt"
    target.write_text("x", encoding="utf-8")
    checker = HealthChecker()

    fake_path = MagicMock()
    fake_path.exists.return_value = True
    fake_path.absolute.return_value = target
    fake_path.stat.side_effect = OSError("stat blew up")

    with patch("qfzz.utils.health.Path", return_value=fake_path):
        result = checker.check_file_exists(str(target), "present")

    assert result["status"] == "unhealthy"
    assert "stat blew up" in result["error"]
