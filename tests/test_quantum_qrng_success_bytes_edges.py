"""QRNG quantum random_bytes success path (eval returns ints)."""

from unittest.mock import MagicMock

from qfzz.quantum.qrng import QuantumRandomNumberGenerator


def test_quantum_random_bytes_success_exact_length_and_masked():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.return_value = 0x1AB  # mask → 0xAB
    qrng = QuantumRandomNumberGenerator(provider=provider)
    data = qrng.random_bytes(3)
    assert isinstance(data, bytes)
    assert len(data) == 3
    assert data == bytes([0xAB, 0xAB, 0xAB])
    assert provider.eval.call_count == 3
    provider.eval.assert_called_with("GenerateRandomInt(8)")
