"""
QFZZ - The Pulse of the Quantum Realm
AI Radio for the Individual

An agentic radio station with quantum security features and edge optimization.
"""

__version__ = "0.1.0"
__author__ = "fuzzywigg"

from qfzz.core.station import QFZZStation
from qfzz.core.config import StationConfig
from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.datasets.manager import DatasetManager
from qfzz.blockchain.trust_network import BlockchainTrustNetwork
from qfzz.edge.optimizer import EdgeOptimizer

__all__ = [
    "QFZZStation",
    "StationConfig",
    "PersonalizedDJ",
    "DatasetManager",
    "BlockchainTrustNetwork",
    "EdgeOptimizer",
]
