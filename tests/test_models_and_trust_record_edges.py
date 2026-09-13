"""Edge coverage for qfzz.blockchain.trust_record Block/TrustRecord dataclasses."""

from datetime import datetime

from qfzz.blockchain.trust_record import Block, TrustRecord


def test_block_calculate_hash_stable():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    b1 = Block(index=1, timestamp=ts, data={"a": 1}, previous_hash="prev")
    b2 = Block(index=1, timestamp=ts, data={"a": 1}, previous_hash="prev")
    assert b1.calculate_hash() == b2.calculate_hash()
    assert len(b1.calculate_hash()) == 64


def test_block_hash_changes_with_data():
    ts = datetime(2024, 1, 1)
    a = Block(index=0, timestamp=ts, data={"x": 1}, previous_hash="0")
    b = Block(index=0, timestamp=ts, data={"x": 2}, previous_hash="0")
    assert a.calculate_hash() != b.calculate_hash()


def test_trust_record_fields():
    rec = TrustRecord(
        user_id="u1",
        action="rating",
        target="track:1",
        trust_delta=0.1,
    )
    assert rec.user_id == "u1"
    assert rec.action == "rating"
    assert rec.target == "track:1"
    assert rec.trust_delta == 0.1
    assert isinstance(rec.timestamp, datetime)
