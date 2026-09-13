"""Extended HealthChecker coverage: ledger, files, degraded paths, JSON."""

import json
from unittest.mock import MagicMock, patch

from qfzz.utils.health import HealthChecker, get_health_checker


class TestHealthLedgerAndFiles:
    def test_ledger_missing_file(self, tmp_path):
        checker = HealthChecker()
        result = checker.check_ledger_integrity(str(tmp_path / "missing.json"))
        assert result["status"] == "unhealthy"
        assert "not found" in result["error"].lower()

    def test_ledger_invalid_json(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{not-json")
        checker = HealthChecker()
        result = checker.check_ledger_integrity(str(path))
        assert result["status"] == "unhealthy"
        assert "Invalid JSON" in result["error"]

    def test_ledger_unexpected_format(self, tmp_path):
        path = tmp_path / "weird.json"
        path.write_text(json.dumps({"foo": 1}))
        checker = HealthChecker()
        result = checker.check_ledger_integrity(str(path))
        assert result["status"] == "degraded"
        assert "Unexpected" in result["error"]

    def test_ledger_list_and_chain_formats(self, tmp_path):
        list_path = tmp_path / "list.json"
        chain_path = tmp_path / "chain.json"
        list_path.write_text(json.dumps([{"i": 0}, {"i": 1}]))
        chain_path.write_text(json.dumps({"chain": [{"i": 0}]}))
        checker = HealthChecker()
        listed = checker.check_ledger_integrity(str(list_path))
        chained = checker.check_ledger_integrity(str(chain_path))
        assert listed["status"] == "healthy"
        assert listed["blocks"] == 2
        assert chained["status"] == "healthy"
        assert chained["blocks"] == 1

    def test_file_exists_present_and_missing(self, tmp_path):
        present = tmp_path / "kg.json"
        present.write_text("{}")
        checker = HealthChecker()
        ok = checker.check_file_exists(str(present), "knowledge_graph")
        missing = checker.check_file_exists(str(tmp_path / "nope"), "audio_content")
        assert ok["status"] == "healthy"
        assert ok["exists"] is True
        assert "size_bytes" in ok
        assert missing["status"] == "degraded"
        assert missing["exists"] is False


class TestHealthDegradedAndJson:
    def test_memory_and_cpu_degraded_thresholds(self):
        checker = HealthChecker()
        with patch("qfzz.utils.health.psutil.virtual_memory") as mem:
            mem.return_value = MagicMock(percent=95.0, available=1, total=100)
            result = checker.check_memory(max_percent=90.0)
            assert result["status"] == "degraded"
        with patch("qfzz.utils.health.psutil.cpu_percent", return_value=99.0):
            cpu = checker.check_cpu(max_percent=90.0)
            assert cpu["status"] == "degraded"

    def test_check_all_degraded_when_only_degraded_checks(self):
        checker = HealthChecker()
        with (
            patch.object(checker, "check_disk_space", return_value={"status": "healthy"}),
            patch.object(checker, "check_memory", return_value={"status": "degraded"}),
            patch.object(checker, "check_cpu", return_value={"status": "healthy"}),
            patch.object(checker, "check_ledger_integrity", return_value={"status": "healthy"}),
            patch.object(checker, "check_file_exists", return_value={"status": "healthy"}),
        ):
            status = checker.check_all()
            assert status.status == "degraded"
            payload = json.loads(checker.to_json(status))
            assert payload["status"] == "degraded"
            assert "checks" in payload

    def test_get_health_checker_singleton(self):
        a = get_health_checker()
        b = get_health_checker()
        assert a is b
        assert isinstance(a, HealthChecker)
