"""QFZZ Station Configuration"""

from dataclasses import dataclass


@dataclass
class StationConfig:
    """Configuration for QFZZ Radio Station
    
    Attributes:
        station_name: Name of the radio station
        station_tagline: Station tagline/slogan
        edge_mode: Enable edge device optimizations
        max_model_size_mb: Maximum model size for edge devices in MB
        enable_6g: Enable 6G network support
        network_protocol: Network protocol to use
        blockchain_enabled: Enable blockchain trust network
        chain_type: Type of blockchain chain
        opensource_datasets_only: Only use opensource datasets
        min_dataset_quality_score: Minimum quality score for datasets (0.0-1.0)
        enable_personalization: Enable personalized DJ features
        community_trust_threshold: Minimum trust score threshold (0.0-1.0)
    """
    station_name: str = "QFZZ"
    station_tagline: str = "The Pulse of the Quantum Realm"
    
    # Edge device settings
    edge_mode: bool = True
    max_model_size_mb: int = 500
    
    # Network settings
    enable_6g: bool = False
    network_protocol: str = "http"
    
    # Blockchain settings
    blockchain_enabled: bool = True
    chain_type: str = "trust_network"
    
    # Dataset settings
    opensource_datasets_only: bool = True
    min_dataset_quality_score: float = 0.7
    
    # DJ personalization
    enable_personalization: bool = True
    community_trust_threshold: float = 0.8
