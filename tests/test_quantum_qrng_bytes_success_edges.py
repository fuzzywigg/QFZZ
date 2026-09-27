"""QRNG quantum bytes success path (eval returns values, no fallback)."""

from unittest.mock import MagicMock

from qfzz.quantum.qrng import QuantumRandomNumberGenerator


def test_quantum_random_bytes_success_masks_to_byte():
    provider = MagicMock()
    provider.is_available = True
    # Values > 255 ensure `& 0xFF` branch is exercised
    provider.eval.side_effect = [300, 1, 512, 255]

    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.is_quantum is True

    data = qrng.random_bytes(4)
    assert data == bytes([300 & 0xFF, 1, 512 & 0xFF, 255])
    assert provider.eval.call_count == 4
