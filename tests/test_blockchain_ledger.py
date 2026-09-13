"""Tests for SovereignLedger hash-chain persistence."""

import json

from qfzz.blockchain.ledger import LedgerBlock, SovereignLedger


class TestSovereignLedger:
    def test_genesis_created_when_missing(self, tmp_path):
        path = tmp_path / "ledger.json"
        ledger = SovereignLedger(str(path))
        assert len(ledger.chain) == 1
        assert ledger.chain[0].event_type == "GENESIS"
        assert path.exists()
        stats = ledger.get_stats()
        assert stats["height"] == 1
        assert stats["status"] == "Verified"

    def test_record_event_appends_and_links(self, tmp_path):
        path = tmp_path / "ledger.json"
        ledger = SovereignLedger(str(path))
        h1 = ledger.record_event("TRACK_PLAY", {"track_id": "t1"})
        h2 = ledger.record_event("TRACK_SKIP", {"track_id": "t1"})
        assert len(ledger.chain) == 3
        assert ledger.chain[1].prev_hash == ledger.chain[0].hash
        assert ledger.chain[2].prev_hash == ledger.chain[1].hash
        assert h1 == ledger.chain[1].hash
        assert h2 == ledger.chain[2].hash
        assert ledger._verify_integrity() is True

    def test_reload_persists_chain(self, tmp_path):
        path = tmp_path / "ledger.json"
        ledger = SovereignLedger(str(path))
        ledger.record_event("PING", {"n": 1})
        reloaded = SovereignLedger(str(path))
        assert len(reloaded.chain) == 2
        assert reloaded.chain[1].event_type == "PING"
        assert reloaded._verify_integrity() is True

    def test_tampered_chain_detected(self, tmp_path):
        path = tmp_path / "ledger.json"
        ledger = SovereignLedger(str(path))
        ledger.record_event("OK", {"x": 1})
        data = json.loads(path.read_text())
        data[1]["data"] = {"x": 999}
        path.write_text(json.dumps(data))
        tampered = SovereignLedger(str(path))
        assert tampered._verify_integrity() is False

    def test_corrupt_file_recreates_genesis(self, tmp_path):
        path = tmp_path / "ledger.json"
        path.write_text("{not-json")
        ledger = SovereignLedger(str(path))
        assert len(ledger.chain) == 1
        assert ledger.chain[0].event_type == "GENESIS"

    def test_ledger_block_to_dict(self):
        block = LedgerBlock(0, "ts", "GENESIS", {}, "0", "abc")
        assert block.to_dict()["hash"] == "abc"
