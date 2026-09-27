"""HealthChecker existing-file metadata and non-JSON ledger exception edges."""

import json
from pathlib import Path
from unittest.mock import patch

from qfzz.utils.health import HealthChecker


def test_check_file_exists_reports_size_and_modified(tmp_path: Path):
    target = tmp_path / "kg.json"
    target.write_text('{"nodes": []}', encoding="utf-8")

    checker = HealthChecker()
    result = checker.check_file_exists(str(target), "knowledge_graph")

    assert result["status"] == "healthy"
    assert result["exists"] is True
    assert result["size_bytes"] == target.stat().st_size
    assert "modified" in result
    assert "T" in result["modified"]  # ISO-ish timestamp


def test_ledger_integrity_generic_exception_is_unhealthy(tmp_path: Path):
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps([{"i": 0}]), encoding="utf-8")

    checker = HealthChecker()
    real_open = open

    def boom(path, *args, **kwargs):
        if Path(path) == ledger:
            raise OSError("permission denied")
        return real_open(path, *args, **kwargs)

    with patch("builtins.open", side_effect=boom):
        result = checker.check_ledger_integrity(str(ledger))

    assert result["status"] == "unhealthy"
    assert "permission denied" in result["error"]
