"""Tests for blockchain trust models and BlockchainTrustNetwork."""

from datetime import datetime

import pytest

from qfzz.blockchain.models import Block, TrustRecord
from qfzz.blockchain.trust_network import BlockchainTrustNetwork
from qfzz.blockchain.trust_record import Block as SimpleBlock
from qfzz.blockchain.trust_record import TrustRecord as SimpleTrustRecord


class TestTrustRecordModel:
    def test_validation(self):
        with pytest.raises(ValueError, match="record_id"):
            TrustRecord(record_id="", content_id="c", creator_id="u", trust_score=0.5)
        with pytest.raises(ValueError, match="trust_score"):
            TrustRecord(record_id="r", content_id="c", creator_id="u", trust_score=2.0)
        with pytest.raises(ValueError, match="verifications"):
            TrustRecord(
                record_id="r", content_id="c", creator_id="u", trust_score=0.5, verifications=-1
            )

    def test_verification_and_report_recalculate_score(self):
        record = TrustRecord(record_id="r1", content_id="c1", creator_id="u1", trust_score=0.5)
        record.add_verification()
        record.add_verification()
        record.add_report()
        assert record.verifications == 2
        assert record.reports == 1
        assert 0.1 <= record.trust_score <= 0.9
        data = record.to_dict()
        assert data["content_id"] == "c1"


class TestBlockModel:
    def test_hash_and_validity(self):
        record = TrustRecord(record_id="r", content_id="c", creator_id="u", trust_score=0.5)
        block = Block(
            index=1, timestamp=datetime.now().isoformat(), records=[record], previous_hash="0"
        )
        assert block.hash
        assert block.is_valid() is True
        block.hash = "tampered"
        assert block.is_valid() is False

    def test_mine_block_difficulty(self):
        block = Block(index=0, timestamp=datetime.now().isoformat(), records=[], previous_hash="0")
        block.mine_block(difficulty=2)
        assert block.hash.startswith("00")
        assert block.nonce >= 0
        assert "records" in block.to_dict()


class TestSimpleTrustRecordModule:
    def test_simple_block_hash(self):
        block = SimpleBlock(index=0, timestamp=datetime.now(), data={"a": 1}, previous_hash="0")
        h = block.calculate_hash()
        assert isinstance(h, str) and len(h) == 64

    def test_simple_trust_record_defaults(self):
        rec = SimpleTrustRecord(user_id="u", action="like", target="t1", trust_delta=0.1)
        assert rec.user_id == "u"
        assert isinstance(rec.timestamp, datetime)


class TestBlockchainTrustNetwork:
    def test_genesis_and_mine(self):
        net = BlockchainTrustNetwork(difficulty=1)
        assert net.get_chain_length() == 1
        assert net.mine_pending_records() is None

        record = net.add_trust_record("content-1", "creator-1", initial_score=0.6)
        assert record.trust_score == 0.6
        block = net.mine_pending_records()
        assert block is not None
        assert net.get_chain_length() == 2
        assert net.is_chain_valid() is True

    def test_verify_report_and_scores(self):
        net = BlockchainTrustNetwork(difficulty=1)
        net.verify_content("c1", "u1")
        net.verify_content("c1", "u1")
        net.report_content("c1", "u1")
        score = net.get_trust_score("c1", "u1")
        assert 0.0 <= score <= 1.0
        assert net.get_trust_score("missing", "x") == 0.5
        assert net.get_creator_trust("u1") == score
        assert net.get_creator_trust("nobody") == 0.5
        assert net.get_trust_record("c1", "u1") is not None

    def test_statistics_and_export(self):
        net = BlockchainTrustNetwork(difficulty=1)
        net.add_trust_record("c1", "u1")
        net.mine_pending_records()
        stats = net.get_statistics()
        assert stats["chain_length"] == 2
        assert stats["is_valid"] is True
        assert stats["total_records"] >= 1
        exported = net.export_chain()
        assert len(exported) == 2
        assert net.get_block(0) is not None
        assert net.get_block(99) is None
        assert net.get_latest_block().index == 1
