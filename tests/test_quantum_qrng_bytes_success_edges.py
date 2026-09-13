"""QRNG quantum random_bytes success path (mocked Q# provider eval)."""

from unittest.mock import MagicMock

from qfzz.quantum.qrng import QuantumRandomNumberGenerator


def test_quantum_random_bytes_success_masks_and_length():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.side_effect = [0x1AB, 0x02, 0xFF]
    qrng = QuantumRandomNumberGenerator(provider=provider)

    assert qrng.is_quantum is True
    assert qrng.backend == "qdk-qrng"

    data = qrng.random_bytes(3)
    assert data == bytes([0xAB, 0x02, 0xFF])
    assert provider.eval.call_count == 3
    for call in provider.eval.call_args_list:
        assert call.args[0] == "GenerateRandomInt(8)"


def test_quantum_backend_name_when_available():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.return_value = 7
    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.backend == "qdk-qrng"
    assert qrng.is_quantum is True
    assert qrng.random_int(8) == 7
