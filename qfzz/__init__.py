"""QFZZ: AI Radio for the Individual - Agentic radio station with quantum security"""

__version__ = "0.1.0"

from qfzz.core.station import QFZZStation
from qfzz.core.config import StationConfig
from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.user_profile import UserProfile
from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.dataset import Dataset, DatasetLicense
from qfzz.blockchain.trust_network import BlockchainTrustNetwork
from qfzz.blockchain.trust_record import TrustRecord, Block
from qfzz.edge.optimizer import EdgeOptimizer
from qfzz.edge.device_config import EdgeDeviceConfig
from qfzz.streaming.player import MusicPlayer

__all__ = [
    "QFZZStation",
    "StationConfig",
    "PersonalizedDJ",
    "UserProfile",
    "DatasetManager",
    "Dataset",
    "DatasetLicense",
    "BlockchainTrustNetwork",
    "TrustRecord",
    "Block",
    "EdgeOptimizer",
    "EdgeDeviceConfig",
    "MusicPlayer",
]
