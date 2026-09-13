"""
Tests for QFZZ quantum module.

Tests the QuantumProvider and QuantumRandomNumberGenerator with
classical fallback (qsharp not required for testing).
"""

import unittest
from unittest.mock import MagicMock, patch

from qfzz.quantum.provider import QuantumProvider
from qfzz.quantum.qrng import QuantumRandomNumberGenerator


class TestQuantumProviderFallback(unittest.TestCase):
    """Test QuantumProvider when qsharp is not available."""

    def test_provider_init_without_qsharp(self):
        """Provider initializes gracefully without qsharp."""
        with patch("qfzz.quantum.provider._is_qsharp_available", return_value=False):
            provider = QuantumProvider()
            self.assertFalse(provider.is_available)
            self.assertEqual(provider.backend_name, "classical-fallback")

    def test_provider_status_without_qsharp(self):
        """Provider reports correct status without qsharp."""
        with patch("qfzz.quantum.provider._is_qsharp_available", return_value=False):
            provider = QuantumProvider()
            status = provider.get_status()
            self.assertEqual(status["backend"], "classical-fallback")
            self.assertFalse(status["available"])
            self.assertFalse(status["qsharp_installed"])

    def test_provider_eval_raises_without_qsharp(self):
        """Provider.eval raises RuntimeError when qsharp not available."""
        with patch("qfzz.quantum.provider._is_qsharp_available", return_value=False):
            provider = QuantumProvider()
            with self.assertRaises(RuntimeError):
                provider.eval("H(q)")


class TestQuantumProviderWithQsharp(unittest.TestCase):
    """Test QuantumProvider when qsharp is available (mocked)."""

    def test_provider_init_with_qsharp(self):
        """Provider initializes with mocked qsharp."""
        mock_qsharp = MagicMock()
        mock_qsharp.__version__ = "1.9.0"
        mock_qsharp.eval = MagicMock(return_value=None)

        with patch("qfzz.quantum.provider._is_qsharp_available", return_value=True), \
             patch("qfzz.quantum.provider._QSHARP_SRC_DIR") as mock_dir:
            mock_dir.glob.return_value = []
            with patch.dict("sys.modules", {"qsharp": mock_qsharp}):
                provider = QuantumProvider()
                self.assertTrue(provider.is_available)
                self.assertEqual(provider.backend_name, "microsoft-qdk")

    def test_provider_status_with_qsharp(self):
        """Provider reports version when qsharp available."""
        mock_qsharp = MagicMock()
        mock_qsharp.__version__ = "1.9.0"
        mock_qsharp.eval = MagicMock(return_value=None)

        with patch("qfzz.quantum.provider._is_qsharp_available", return_value=True), \
             patch("qfzz.quantum.provider._QSHARP_SRC_DIR") as mock_dir:
            mock_dir.glob.return_value = []
            with patch.dict("sys.modules", {"qsharp": mock_qsharp}):
                provider = QuantumProvider()
                status = provider.get_status()
                self.assertEqual(status["qsharp_version"], "1.9.0")
                self.assertTrue(status["available"])


class TestQRNGFallback(unittest.TestCase):
    """Test QuantumRandomNumberGenerator with classical fallback."""

    def setUp(self):
        """Create QRNG with classical fallback."""
        with patch("qfzz.quantum.provider._is_qsharp_available", return_value=False):
            provider = QuantumProvider()
            self.qrng = QuantumRandomNumberGenerator(provider=provider)

    def test_qrng_uses_classical_fallback(self):
        """QRNG uses classical backend when qsharp not available."""
        self.assertFalse(self.qrng.is_quantum)
        self.assertEqual(self.qrng.backend, "classical-csprng")

    def test_random_int_range(self):
        """random_int returns values in valid range."""
        for n_bits in [1, 8, 16, 32]:
            value = self.qrng.random_int(n_bits)
            self.assertGreaterEqual(value, 0)
            self.assertLess(value, 2 ** n_bits)

    def test_random_int_invalid_bits(self):
        """random_int raises ValueError for invalid n_bits."""
        with self.assertRaises(ValueError):
            self.qrng.random_int(0)
        with self.assertRaises(ValueError):
            self.qrng.random_int(65)

    def test_random_bytes_length(self):
        """random_bytes returns correct number of bytes."""
        for n in [1, 16, 32]:
            result = self.qrng.random_bytes(n)
            self.assertIsInstance(result, bytes)
            self.assertEqual(len(result), n)

    def test_random_bytes_invalid(self):
        """random_bytes raises ValueError for invalid input."""
        with self.assertRaises(ValueError):
            self.qrng.random_bytes(0)

    def test_random_nonce(self):
        """random_nonce returns valid 32-bit integer."""
        nonce = self.qrng.random_nonce()
        self.assertIsInstance(nonce, int)
        self.assertGreaterEqual(nonce, 0)
        self.assertLess(nonce, 2 ** 32)

    def test_random_int_not_constant(self):
        """random_int produces varying values (statistical test)."""
        values = {self.qrng.random_int(32) for _ in range(10)}
        self.assertGreater(len(values), 1)


class TestQRNGWithMockedQuantum(unittest.TestCase):
    """Test QRNG with mocked quantum provider."""

    def test_qrng_uses_quantum_when_available(self):
        """QRNG uses quantum backend when provider is available."""
        mock_provider = MagicMock()
        mock_provider.is_available = True
        mock_provider.eval = MagicMock(return_value=42)

        qrng = QuantumRandomNumberGenerator(provider=mock_provider)
        self.assertTrue(qrng.is_quantum)
        self.assertEqual(qrng.backend, "qdk-qrng")

    def test_quantum_random_int(self):
        """random_int calls provider.eval with correct Q# code."""
        mock_provider = MagicMock()
        mock_provider.is_available = True
        mock_provider.eval = MagicMock(return_value=42)

        qrng = QuantumRandomNumberGenerator(provider=mock_provider)
        result = qrng.random_int(8)

        mock_provider.eval.assert_called_with("GenerateRandomInt(8)")
        self.assertEqual(result, 42)

    def test_quantum_fallback_on_error(self):
        """QRNG falls back to classical on quantum error."""
        mock_provider = MagicMock()
        mock_provider.is_available = True
        mock_provider.eval = MagicMock(side_effect=RuntimeError("Quantum error"))

        qrng = QuantumRandomNumberGenerator(provider=mock_provider)
        result = qrng.random_int(8)

        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 256)


class TestBlockMiningWithQRNG(unittest.TestCase):
    """Test blockchain Block mining with QRNG integration."""

    def test_mine_block_with_qrng(self):
        """Block mining works with QRNG for nonce seeding."""
        from qfzz.blockchain.models import Block

        mock_qrng = MagicMock()
        mock_qrng.random_nonce = MagicMock(return_value=1000)

        block = Block(
            index=1,
            timestamp="2026-01-01T00:00:00",
            records=[],
            previous_hash="abc123",
        )

        block.mine_block(difficulty=1, qrng=mock_qrng)

        mock_qrng.random_nonce.assert_called_once()
        self.assertTrue(block.hash.startswith("0"))
        self.assertTrue(block.is_valid())

    def test_mine_block_without_qrng(self):
        """Block mining still works without QRNG (backward compatible)."""
        from qfzz.blockchain.models import Block

        block = Block(
            index=1,
            timestamp="2026-01-01T00:00:00",
            records=[],
            previous_hash="abc123",
        )

        block.mine_block(difficulty=1)

        self.assertTrue(block.hash.startswith("0"))
        self.assertTrue(block.is_valid())


class TestStationConfigQuantum(unittest.TestCase):
    """Test StationConfig quantum flag."""

    def test_config_quantum_default_false(self):
        """Quantum is disabled by default."""
        from qfzz.core.config import StationConfig

        config = StationConfig(station_id="test", station_name="Test")
        self.assertFalse(config.enable_quantum)

    def test_config_quantum_enabled(self):
        """Quantum can be enabled via config."""
        from qfzz.core.config import StationConfig

        config = StationConfig(station_id="test", station_name="Test", enable_quantum=True)
        self.assertTrue(config.enable_quantum)

    def test_config_quantum_in_dict(self):
        """Quantum flag appears in config dict."""
        from qfzz.core.config import StationConfig

        config = StationConfig(station_id="test", station_name="Test", enable_quantum=True)
        d = config.to_dict()
        self.assertIn("enable_quantum", d)
        self.assertTrue(d["enable_quantum"])


if __name__ == "__main__":
    unittest.main()
