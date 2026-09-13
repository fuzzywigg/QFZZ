"""QRNG quantum eval-failure falls back to classical int/bytes."""

from unittest.mock import MagicMock

from qfzz.quantum.qrng import QuantumRandomNumberGenerator


def test_quantum_random_int_falls_back_on_eval_error():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.side_effect = RuntimeError("q# boom")
    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.is_quantum is True
    val = qrng.random_int(8)
    assert 0 <= val < 256
    provider.eval.assert_called()


def test_quantum_random_bytes_falls_back_on_eval_error():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.side_effect = RuntimeError("q# boom")
    qrng = QuantumRandomNumberGenerator(provider=provider)
    data = qrng.random_bytes(4)
    assert isinstance(data, bytes)
    assert len(data) == 4


def test_classical_backend_and_nonce():
    provider = MagicMock()
    provider.is_available = False
    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.backend == "classical-csprng"
    nonce = qrng.random_nonce()
    assert isinstance(nonce, int)
    assert 0 <= nonce < 2**32
