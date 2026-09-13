"""Invalid-chain and auto-create edges for BlockchainTrustNetwork."""

from qfzz.blockchain.trust_network import BlockchainTrustNetwork


def test_is_chain_valid_detects_tampered_hash():
    net = BlockchainTrustNetwork(difficulty=1)
    net.add_trust_record("c1", "u1", initial_score=0.6)
    net.mine_pending_records()
    assert net.is_chain_valid() is True
    net._chain[1].hash = "deadbeef"
    assert net.is_chain_valid() is False


def test_is_chain_valid_detects_broken_previous_hash():
    net = BlockchainTrustNetwork(difficulty=1)
    net.add_trust_record("c2", "u2")
    net.mine_pending_records()
    net._chain[1].previous_hash = "not-the-genesis"
    assert net.is_chain_valid() is False


def test_verify_and_report_auto_create_and_metadata():
    net = BlockchainTrustNetwork(difficulty=1)
    assert net.get_trust_record("new", "creator") is None
    net.verify_content("new", "creator")
    record = net.get_trust_record("new", "creator")
    assert record is not None
    assert record.verifications >= 1

    net.report_content("new", "creator")
    assert record.reports >= 1

    rec2 = net.add_trust_record("c3", "u3", metadata={"k": 1})
    assert rec2.metadata.get("k") == 1
    mined = net.mine_pending_records()
    assert mined is not None
    # pending cleared
    assert net.mine_pending_records() is None
