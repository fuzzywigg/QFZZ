"""Edge cases for BlockchainTrustNetwork: empty chain, invalid inputs,
duplicate keys, mine idempotency, and export serialization round-trips.
"""

from datetime import datetime

import pytest

from qfzz.blockchain.models import Block, TrustRecord
from qfzz.blockchain.trust_network import BlockchainTrustNetwork
from qfzz.blockchain.trust_record import Block as SimpleBlock
from qfzz.blockchain.trust_record import TrustRecord as SimpleTrustRecord


@pytest.fixture
def empty_net() -> BlockchainTrustNetwork:
    """Fresh network with genesis only (no pending records)."""
    return BlockchainTrustNetwork(difficulty=1)


@pytest.fixture
def net_with_pending(empty_net: BlockchainTrustNetwork) -> BlockchainTrustNetwork:
    """Network with one pending trust record ready to mine."""
    empty_net.add_trust_record(
        "content-a",
        "creator-a",
        initial_score=0.6,
        metadata={"src": "edge"},
    )
    return empty_net


class TestEmptyChainEdges:
    def test_genesis_only_stats_and_validity(self, empty_net: BlockchainTrustNetwork):
        assert empty_net.get_chain_length() == 1
        assert empty_net.is_chain_valid() is True
        stats = empty_net.get_statistics()
        assert stats["chain_length"] == 1
        assert stats["total_records"] == 0
        assert stats["pending_records"] == 0
        assert stats["indexed_records"] == 0
        assert stats["difficulty"] == 1
        assert stats["is_valid"] is True

    def test_get_block_rejects_negative_and_oob(self, empty_net: BlockchainTrustNetwork):
        assert empty_net.get_block(0) is not None
        assert empty_net.get_block(-1) is None
        assert empty_net.get_block(1) is None

    def test_latest_block_is_genesis(self, empty_net: BlockchainTrustNetwork):
        latest = empty_net.get_latest_block()
        assert latest.index == 0
        assert latest.previous_hash == "0"
        assert latest.records == []

    def test_mine_empty_pending_is_idempotent(self, empty_net: BlockchainTrustNetwork):
        assert empty_net.mine_pending_records() is None
        assert empty_net.mine_pending_records() is None
        assert empty_net.get_chain_length() == 1


class TestInvalidInputEdges:
    def test_add_trust_record_rejects_out_of_range_score(
        self, empty_net: BlockchainTrustNetwork
    ):
        with pytest.raises(ValueError, match="trust_score"):
            empty_net.add_trust_record("c", "u", initial_score=1.5)
        with pytest.raises(ValueError, match="trust_score"):
            empty_net.add_trust_record("c", "u", initial_score=-0.1)
        assert empty_net.get_statistics()["pending_records"] == 0
        assert empty_net.get_trust_record("c", "u") is None

    def test_boundary_scores_zero_and_one(self, empty_net: BlockchainTrustNetwork):
        low = empty_net.add_trust_record("low", "u", initial_score=0.0)
        high = empty_net.add_trust_record("high", "u", initial_score=1.0)
        assert low.trust_score == 0.0
        assert high.trust_score == 1.0
        assert empty_net.get_trust_score("low", "u") == 0.0
        assert empty_net.get_trust_score("high", "u") == 1.0


class TestDuplicateKeyAndMineIdempotency:
    def test_duplicate_content_creator_overwrites_index(
        self, empty_net: BlockchainTrustNetwork
    ):
        first = empty_net.add_trust_record("same", "pair", initial_score=0.3)
        second = empty_net.add_trust_record("same", "pair", initial_score=0.9)
        assert first.record_id != second.record_id
        # Index keeps the latest record for the content:creator key
        indexed = empty_net.get_trust_record("same", "pair")
        assert indexed is second
        assert empty_net.get_trust_score("same", "pair") == 0.9
        # Both remain pending until mined
        assert empty_net.get_statistics()["pending_records"] == 2

    def test_mine_then_remine_idempotent_and_scores_stable(
        self, net_with_pending: BlockchainTrustNetwork
    ):
        score_before = net_with_pending.get_trust_score("content-a", "creator-a")
        block = net_with_pending.mine_pending_records()
        assert block is not None
        assert net_with_pending.mine_pending_records() is None
        assert net_with_pending.mine_pending_records() is None
        assert net_with_pending.get_trust_score("content-a", "creator-a") == score_before
        assert net_with_pending.is_chain_valid() is True

    def test_sequential_mines_keep_chain_valid(self, empty_net: BlockchainTrustNetwork):
        empty_net.add_trust_record("c1", "u1", initial_score=0.4)
        b1 = empty_net.mine_pending_records()
        empty_net.add_trust_record("c2", "u1", initial_score=0.8)
        b2 = empty_net.mine_pending_records()
        assert b1 is not None and b2 is not None
        assert b2.previous_hash == b1.hash
        assert empty_net.get_chain_length() == 3
        assert empty_net.is_chain_valid() is True
        assert abs(empty_net.get_creator_trust("u1") - 0.6) < 1e-9


class TestExportSerializationRoundTrip:
    def test_export_chain_round_trips_record_fields(
        self, net_with_pending: BlockchainTrustNetwork
    ):
        mined = net_with_pending.mine_pending_records()
        assert mined is not None
        exported = net_with_pending.export_chain()
        assert len(exported) == 2

        genesis, block1 = exported
        assert genesis["index"] == 0
        assert genesis["records"] == []
        assert block1["index"] == 1
        assert len(block1["records"]) == 1

        rec_dict = block1["records"][0]
        rebuilt = TrustRecord(
            record_id=rec_dict["record_id"],
            content_id=rec_dict["content_id"],
            creator_id=rec_dict["creator_id"],
            trust_score=rec_dict["trust_score"],
            verifications=rec_dict["verifications"],
            reports=rec_dict["reports"],
            metadata=dict(rec_dict["metadata"]),
            created_at=rec_dict["created_at"],
            updated_at=rec_dict["updated_at"],
        )
        assert rebuilt.to_dict() == rec_dict
        assert rebuilt.metadata["src"] == "edge"

        # Reconstruct block and verify hash matches exported hash
        rebuilt_block = Block(
            index=block1["index"],
            timestamp=block1["timestamp"],
            records=[rebuilt],
            previous_hash=block1["previous_hash"],
            nonce=block1["nonce"],
            hash=block1["hash"],
        )
        assert rebuilt_block.is_valid() is True
        assert rebuilt_block.hash == block1["hash"]
        assert rebuilt_block.previous_hash == genesis["hash"]


class TestSimpleTrustRecordModuleEdges:
    def test_simple_block_hash_sensitive_to_index_and_previous(
        self,
    ):
        ts = datetime(2026, 3, 15, 8, 30, 0)
        base = SimpleBlock(index=1, timestamp=ts, data={"k": "v"}, previous_hash="aaa")
        h = base.calculate_hash()

        other_index = SimpleBlock(index=2, timestamp=ts, data={"k": "v"}, previous_hash="aaa")
        other_prev = SimpleBlock(index=1, timestamp=ts, data={"k": "v"}, previous_hash="bbb")
        other_ts = SimpleBlock(
            index=1,
            timestamp=datetime(2026, 3, 15, 8, 30, 1),
            data={"k": "v"},
            previous_hash="aaa",
        )
        empty_data = SimpleBlock(index=1, timestamp=ts, data={}, previous_hash="aaa")

        assert other_index.calculate_hash() != h
        assert other_prev.calculate_hash() != h
        assert other_ts.calculate_hash() != h
        assert empty_data.calculate_hash() != h

    def test_simple_trust_record_explicit_timestamp_and_negative_delta(self):
        ts = datetime(2025, 12, 1, 0, 0, 0)
        rec = SimpleTrustRecord(
            user_id="u",
            action="verification",
            target="content:9",
            trust_delta=-0.25,
            timestamp=ts,
        )
        assert rec.timestamp == ts
        assert rec.trust_delta == -0.25
        assert rec.action == "verification"
