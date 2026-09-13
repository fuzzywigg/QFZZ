"""Ledger / to_json / singleton / degraded edges for HealthChecker."""

import json
from pathlib import Path
from unittest.mock import patch

from qfzz.utils.health import HealthChecker, get_health_checker


def test_ledger_missing_corrupt_and_formats(tmp_path: Path):
    checker = HealthChecker()
    missing = checker.check_ledger_integrity(str(tmp_path / "nope.json"))
    assert missing["status"] == "unhealthy"
    assert "not found" in missing["error"].lower()

    bad = tmp_path / "bad.json"
    bad.write_text("{broken", encoding="utf-8")
    corrupt = checker.check_ledger_integrity(str(bad))
    assert corrupt["status"] == "unhealthy"
    assert "Invalid JSON" in corrupt["error"]

    weird = tmp_path / "weird.json"
    weird.write_text(json.dumps({"foo": 1}), encoding="utf-8")
    degraded = checker.check_ledger_integrity(str(weird))
    assert degraded["status"] == "degraded"

    chain = tmp_path / "chain.json"
    chain.write_text(json.dumps({"chain": [{"i": 0}, {"i": 1}]}), encoding="utf-8")
    ok = checker.check_ledger_integrity(str(chain))
    assert ok["status"] == "healthy"
    assert ok["blocks"] == 2

    listed = tmp_path / "list.json"
    listed.write_text(json.dumps([{"i": 0}]), encoding="utf-8")
    ok_list = checker.check_ledger_integrity(str(listed))
    assert ok_list["status"] == "healthy"
    assert ok_list["blocks"] == 1


def test_memory_cpu_oserror_and_degraded_overall():
    checker = HealthChecker()
    with patch("qfzz.utils.health.psutil.virtual_memory", side_effect=OSError("mem")):
        mem = checker.check_memory()
        assert mem["status"] == "unhealthy"
    with patch("qfzz.utils.health.psutil.cpu_percent", side_effect=OSError("cpu")):
        cpu = checker.check_cpu()
        assert cpu["status"] == "unhealthy"

    with (
        patch.object(checker, "check_disk_space", return_value={"status": "healthy"}),
        patch.object(checker, "check_memory", return_value={"status": "healthy"}),
        patch.object(checker, "check_cpu", return_value={"status": "degraded"}),
        patch.object(checker, "check_ledger_integrity", return_value={"status": "healthy"}),
        patch.object(checker, "check_file_exists", return_value={"status": "healthy"}),
    ):
        status = checker.check_all()
        assert status.status == "degraded"
        payload = json.loads(checker.to_json(status))
        assert payload["status"] == "degraded"


def test_get_health_checker_singleton():
    import qfzz.utils.health as health_mod

    health_mod._health_checker = None
    a = get_health_checker()
    b = get_health_checker()
    assert a is b
    assert isinstance(a, HealthChecker)
