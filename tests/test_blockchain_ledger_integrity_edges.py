"""Edge coverage for SovereignLedger integrity links, save failures, and hash stability."""

import json
from pathlib import Path
from unittest.mock import patch

from qfzz.blockchain.ledger import SovereignLedger


def test_prev_hash_mismatch_breaks_integrity(tmp_path: Path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    ledger.record_event("PLAY", {"id": 1})
    ledger.record_event("SKIP", {"id": 1})

    data = json.loads(path.read_text())
    data[2]["prev_hash"] = "0" * 64
    path.write_text(json.dumps(data))

    reloaded = SovereignLedger(str(path))
    assert len(reloaded.chain) == 3  # soft-fork: still loads
    assert reloaded._verify_integrity() is False


def test_save_oserror_does_not_crash_record_event(tmp_path: Path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    with patch("builtins.open", side_effect=OSError("disk full")):
        # In-memory append still happens; persistence failure is logged
        h = ledger.record_event("PING", {"n": 1})
    assert isinstance(h, str)
    assert len(h) == 64
    assert len(ledger.chain) == 2


def test_hash_stability_sort_keys(tmp_path: Path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    h1 = ledger._calculate_hash(1, "ts", "EVT", {"b": 2, "a": 1}, "prev")
    h2 = ledger._calculate_hash(1, "ts", "EVT", {"a": 1, "b": 2}, "prev")
    assert h1 == h2


def test_content_hash_mismatch_distinct_from_link_break(tmp_path: Path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    ledger.record_event("OK", {"x": 1})
    data = json.loads(path.read_text())
    data[1]["hash"] = "deadbeef" * 8
    path.write_text(json.dumps(data))
    tampered = SovereignLedger(str(path))
    assert tampered._verify_integrity() is False


def test_get_stats_after_events(tmp_path: Path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    ledger.record_event("A", {})
    stats = ledger.get_stats()
    assert stats["height"] == 2
    assert stats["last_hash"] == ledger.chain[-1].hash
    assert stats["status"] == "Verified"
