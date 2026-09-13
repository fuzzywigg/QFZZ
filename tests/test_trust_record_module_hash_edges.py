"""Simple trust_record.Block hash determinism edges (not blockchain.models)."""

from datetime import datetime

from qfzz.blockchain.trust_record import Block, TrustRecord


def test_block_hash_deterministic_and_changes_with_data():
    ts = datetime(2026, 1, 1, 12, 0, 0)
    block = Block(
        index=1,
        timestamp=ts,
        data={"event": "play", "track": "pulse"},
        previous_hash="abc123",
    )
    h1 = block.calculate_hash()
    h2 = block.calculate_hash()
    assert h1 == h2
    assert len(h1) == 64

    block.data = {"event": "play", "track": "other"}
    assert block.calculate_hash() != h1


def test_trust_record_defaults_timestamp():
    rec = TrustRecord(
        user_id="u1",
        action="rating",
        target="track:1",
        trust_delta=0.1,
    )
    assert rec.user_id == "u1"
    assert rec.action == "rating"
    assert rec.trust_delta == 0.1
    assert isinstance(rec.timestamp, datetime)
