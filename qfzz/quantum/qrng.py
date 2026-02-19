"""
Quantum Random Number Generator using Microsoft QDK.

Provides quantum-enhanced random number generation for cryptographic
operations in the QFZZ blockchain trust network. Falls back to
classical CSPRNG (os.urandom) when qsharp is not available.
"""

import logging
import os
from typing import Optional

from .provider import QuantumProvider

logger = logging.getLogger(__name__)


class QuantumRandomNumberGenerator:
    """
    Quantum Random Number Generator (QRNG) powered by Microsoft QDK.

    Uses Q# quantum operations to generate truly random numbers via
    qubit superposition and measurement. When the qsharp package is
    not available, falls back to a cryptographically secure classical
    PRNG (os.urandom).
    """

    def __init__(self, provider: Optional[QuantumProvider] = None):
        """
        Initialize the QRNG.

        Args:
            provider: Optional QuantumProvider instance. If None, creates one.
        """
        self._provider = provider or QuantumProvider()
        self._use_quantum = self._provider.is_available

        if self._use_quantum:
            logger.info("QRNG initialized with Microsoft QDK backend")
        else:
            logger.info("QRNG initialized with classical CSPRNG fallback")

    @property
    def is_quantum(self) -> bool:
        """Check if quantum random generation is active."""
        return self._use_quantum

    @property
    def backend(self) -> str:
        """Get the active backend name."""
        return "qdk-qrng" if self._use_quantum else "classical-csprng"

    def random_int(self, n_bits: int = 32) -> int:
        """
        Generate a random integer using n_bits of randomness.

        Args:
            n_bits: Number of random bits (1-64)

        Returns:
            Random integer in range [0, 2^n_bits - 1]

        Raises:
            ValueError: If n_bits is out of valid range
        """
        if not 1 <= n_bits <= 64:
            raise ValueError("n_bits must be between 1 and 64")

        if self._use_quantum:
            return self._quantum_random_int(n_bits)
        return self._classical_random_int(n_bits)

    def random_bytes(self, n_bytes: int = 32) -> bytes:
        """
        Generate random bytes.

        Args:
            n_bytes: Number of random bytes to generate

        Returns:
            Random bytes

        Raises:
            ValueError: If n_bytes is not positive
        """
        if n_bytes < 1:
            raise ValueError("n_bytes must be positive")

        if self._use_quantum:
            return self._quantum_random_bytes(n_bytes)
        return os.urandom(n_bytes)

    def random_nonce(self) -> int:
        """
        Generate a random nonce suitable for blockchain mining.

        Returns:
            Random 32-bit integer for use as a starting nonce
        """
        return self.random_int(32)

    def _quantum_random_int(self, n_bits: int) -> int:
        """Generate random int using Q# quantum operations."""
        try:
            result = self._provider.eval(f"GenerateRandomInt({n_bits})")
            return int(result)
        except Exception as e:
            logger.warning(f"Quantum random generation failed, using classical fallback: {e}")
            return self._classical_random_int(n_bits)

    def _quantum_random_bytes(self, n_bytes: int) -> bytes:
        """Generate random bytes using Q# quantum operations."""
        try:
            result_bytes = []
            for _ in range(n_bytes):
                val = self._provider.eval("GenerateRandomInt(8)")
                result_bytes.append(int(val) & 0xFF)
            return bytes(result_bytes)
        except Exception as e:
            logger.warning(f"Quantum random generation failed, using classical fallback: {e}")
            return os.urandom(n_bytes)

    @staticmethod
    def _classical_random_int(n_bits: int) -> int:
        """Generate random int using classical CSPRNG."""
        n_bytes = (n_bits + 7) // 8
        raw = os.urandom(n_bytes)
        value = int.from_bytes(raw, byteorder="big")
        # Mask to exact number of bits
        mask = (1 << n_bits) - 1
        return value & mask
