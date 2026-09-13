"""TrustNetwork.get_block negative index edge."""

from qfzz.blockchain.trust_network import BlockchainTrustNetwork


def test_get_block_negative_index_returns_none():
    net = BlockchainTrustNetwork(difficulty=1)
    assert net.get_block(-1) is None
    assert net.get_block(0) is not None  # genesis
