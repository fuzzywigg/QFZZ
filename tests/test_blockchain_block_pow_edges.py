"""Blockchain Block PoW / integrity and TrustRecord score-bound edges."""

from datetime import datetime

from qfzz.blockchain.models import Block, TrustRecord


def test_block_tamper_invalidates_hash():
    record = TrustRecord(
        record_id="r1",
        content_id="c1",
        creator_id="u1",
        trust_score=0.5,
    )
    block = Block(
        index=1,
        timestamp=datetime.now().isoformat(),
        records=[record],
        previous_hash="0" * 64,
    )
    assert block.is_valid() is True
    block.records[0].trust_score = 0.9
    assert block.is_valid() is False


def test_mine_block_difficulty_zero_immediate():
    block = Block(
        index=0,
        timestamp=datetime.now().isoformat(),
        records=[],
        previous_hash="genesis",
    )
    block.mine_block(difficulty=0)
    assert block.is_valid() is True
    assert block.hash == block.calculate_hash()


def test_trust_score_bounds_all_reports_and_verifications():
    rec = TrustRecord(
        record_id="r2",
        content_id="c2",
        creator_id="u2",
        trust_score=0.5,
    )
    rec.add_report()
    assert abs(rec.trust_score - 0.1) < 1e-9

    rec2 = TrustRecord(
        record_id="r3",
        content_id="c3",
        creator_id="u3",
        trust_score=0.5,
    )
    rec2.add_verification()
    assert abs(rec2.trust_score - 0.9) < 1e-9


def test_block_to_dict_roundtrip_shape():
    rec = TrustRecord(
        record_id="r4",
        content_id="c4",
        creator_id="u4",
        trust_score=0.6,
    )
    block = Block(
        index=2,
        timestamp="2026-01-01T00:00:00",
        records=[rec],
        previous_hash="abc",
    )
    data = block.to_dict()
    assert data["index"] == 2
    assert data["previous_hash"] == "abc"
    assert len(data["records"]) == 1
    assert data["records"][0]["record_id"] == "r4"
    assert data["hash"] == block.hash
