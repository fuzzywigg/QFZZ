"""Ledger content-hash mismatch with intact prev_hash link."""

import json

from qfzz.blockchain.ledger import SovereignLedger


def test_content_hash_mismatch_detected_with_valid_prev_link(tmp_path):
    path = tmp_path / "ledger.json"
    ledger = SovereignLedger(str(path))
    ledger.record_event("OK", {"n": 1})
    data = json.loads(path.read_text())
    # Keep prev_hash link intact; only mutate payload so recalc hash fails
    data[1]["data"] = {"n": 999, "tampered": True}
    path.write_text(json.dumps(data))
    reloaded = SovereignLedger(str(path))
    assert reloaded._verify_integrity() is False
    assert reloaded.chain[1].prev_hash == reloaded.chain[0].hash
