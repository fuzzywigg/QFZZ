"""Edge Device Configuration"""

from dataclasses import dataclass


@dataclass
class EdgeDeviceConfig:
    """Configuration for edge device deployment
    
    Attributes:
        device_id: Unique device identifier
        device_type: Type of device (e.g., "smartphone", "smart_speaker", "embedded")
        max_memory_mb: Maximum available memory in MB
        max_model_size_mb: Maximum model size in MB
        enable_6g: Enable 6G network features
        network_bandwidth_mbps: Network bandwidth in Mbps
        storage_available_gb: Available storage in GB
    """
    device_id: str
    device_type: str
    max_memory_mb: int = 512
    max_model_size_mb: int = 100
    enable_6g: bool = False
    network_bandwidth_mbps: int = 100
    storage_available_gb: float = 1.0
