"""
QFZZ Quantum Module

Quantum-enhanced capabilities powered by the Microsoft Quantum Development Kit (QDK).
Provides quantum random number generation and resource estimation via the qsharp package.
"""

from .provider import QuantumProvider
from .qrng import QuantumRandomNumberGenerator

__all__ = ["QuantumProvider", "QuantumRandomNumberGenerator"]
