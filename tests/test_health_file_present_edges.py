"""HealthChecker check_file_exists healthy path when file is present."""

from qfzz.utils.health import HealthChecker


def test_check_file_exists_present_reports_size_and_modified(tmp_path):
    target = tmp_path / "present.cfg"
    target.write_text("ok", encoding="utf-8")
    checker = HealthChecker()
    result = checker.check_file_exists(str(target), "cfg")
    assert result["status"] == "healthy"
    assert result["exists"] is True
    assert result["size_bytes"] == 2
    assert "modified" in result
    assert str(target.resolve()) in result["path"] or result["path"].endswith("present.cfg")
