"""Ledger prev_hash break, soft save failure, and reload integrity edges."""

import json
from unittest.mock import patch

from qfzz.blockchain.ledger import SovereignLedger


def test_broken_prev_hash_link_detected(tmp_path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    ledger.record_event("OK", {"n": 1})
    data = json.loads(path.read_text())
    data[1]["prev_hash"] = "0" * 64
    path.write_text(json.dumps(data))
    reloaded = SovereignLedger(str(path))
    assert reloaded._verify_integrity() is False
    assert len(reloaded.chain) >= 2


def test_save_ledger_oserror_soft_fails(tmp_path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    before = len(ledger.chain)
    with patch("builtins.open", side_effect=OSError("disk full")):
        h = ledger.record_event("SOFT", {"x": 1})
    assert h
    assert len(ledger.chain) == before + 1
    assert ledger._verify_integrity() is True


def test_integrity_true_on_valid_multi_block_chain(tmp_path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    ledger.record_event("A", {"i": 1})
    ledger.record_event("B", {"i": 2})
    assert ledger._verify_integrity() is True
    stats = ledger.get_stats()
    assert stats["height"] == 3
    assert stats["status"] == "Verified"
