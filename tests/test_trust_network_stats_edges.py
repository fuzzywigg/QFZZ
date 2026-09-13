"""BlockchainTrustNetwork multi-creator average, metadata, mine, stats edges."""

from qfzz.blockchain.trust_network import BlockchainTrustNetwork


def test_creator_trust_averages_multiple_contents():
    net = BlockchainTrustNetwork(difficulty=1)
    net.add_trust_record("c1", "creator-a", initial_score=0.2)
    net.add_trust_record("c2", "creator-a", initial_score=0.8)
    net.add_trust_record("c3", "other", initial_score=1.0)
    assert abs(net.get_creator_trust("creator-a") - 0.5) < 1e-9
    assert abs(net.get_creator_trust("missing") - 0.5) < 1e-9


def test_add_trust_record_stores_metadata():
    net = BlockchainTrustNetwork(difficulty=1)
    rec = net.add_trust_record(
        "content-x",
        "creator-y",
        initial_score=0.7,
        metadata={"source": "unit-test", "note": "edge"},
    )
    assert rec.metadata["source"] == "unit-test"
    stored = net.get_trust_record("content-x", "creator-y")
    assert stored is not None
    assert stored.metadata["note"] == "edge"
    assert abs(net.get_trust_score("content-x", "creator-y") - 0.7) < 1e-9


def test_mine_clears_pending_and_stats_index():
    net = BlockchainTrustNetwork(difficulty=1)
    net.add_trust_record("a", "c", initial_score=0.6)
    net.add_trust_record("b", "c", initial_score=0.4)
    stats_before = net.get_statistics()
    assert stats_before["pending_records"] == 2
    assert stats_before["indexed_records"] == 2

    block = net.mine_pending_records()
    assert block is not None
    assert block.index == 1
    stats = net.get_statistics()
    assert stats["pending_records"] == 0
    assert stats["chain_length"] == 2
    assert stats["total_records"] == 2
    assert stats["indexed_records"] == 2
    assert stats["is_valid"] is True
    assert net.mine_pending_records() is None
