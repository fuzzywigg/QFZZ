"""Edge coverage for QRNG quantum bytes/int fallbacks and QuantumProvider init/status."""

from unittest.mock import MagicMock, patch

from qfzz.quantum.provider import QuantumProvider
from qfzz.quantum.qrng import QuantumRandomNumberGenerator


def test_random_bytes_quantum_success_and_failure_fallback():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.side_effect = [10, 20, 30]
    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.is_quantum is True
    assert qrng.backend == "qdk-qrng"
    out = qrng.random_bytes(3)
    assert out == bytes([10, 20, 30])

    provider.eval.side_effect = RuntimeError("eval fail")
    fallback = qrng.random_bytes(4)
    assert isinstance(fallback, bytes)
    assert len(fallback) == 4


def test_random_int_boundaries_and_quantum_fallback():
    provider = MagicMock()
    provider.is_available = True
    provider.eval.return_value = 7
    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.random_int(1) == 7
    assert qrng.random_int(64) == 7

    provider.eval.side_effect = RuntimeError("q fail")
    value = qrng.random_int(8)
    assert 0 <= value <= 255


def test_classical_backend_when_unavailable():
    provider = MagicMock()
    provider.is_available = False
    qrng = QuantumRandomNumberGenerator(provider=provider)
    assert qrng.is_quantum is False
    assert qrng.backend == "classical-csprng"
    assert len(qrng.random_bytes(8)) == 8
    assert isinstance(qrng.random_nonce(), int)


def test_provider_init_failure_and_version_unknown():
    fake_qsharp = MagicMock()
    del fake_qsharp.__version__
    fake_qsharp.eval.side_effect = RuntimeError("bad qs")

    with patch("qfzz.quantum.provider._is_qsharp_available", return_value=True):
        with patch.dict("sys.modules", {"qsharp": fake_qsharp}):
            with patch("qfzz.quantum.provider._QSHARP_SRC_DIR") as src:
                qs = MagicMock()
                qs.read_text.return_value = "operation X() : Unit {}"
                src.glob.return_value = [qs]
                provider = QuantumProvider()
                assert provider.is_available is False
                assert provider.backend_name == "classical-fallback"
                status = provider.get_status()
                assert status["available"] is False
                assert status["qsharp_installed"] is True


def test_provider_status_unknown_version_when_initialized():
    provider = QuantumProvider.__new__(QuantumProvider)
    provider._initialized = True
    provider._qsharp_available = True
    qsharp = MagicMock(spec=[])  # no __version__
    provider._qsharp = qsharp
    status = provider.get_status()
    assert status["backend"] == "microsoft-qdk"
    assert status["qsharp_version"] == "unknown"
