"""
Configuration for edge devices.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum


class DeviceType(Enum):
    """Supported edge device types."""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    IOT = "iot"
    SMART_SPEAKER = "smart_speaker"
    CAR_SYSTEM = "car_system"


class NetworkType(Enum):
    """Network connection types."""
    WIFI = "wifi"
    CELLULAR_5G = "5g"
    CELLULAR_4G = "4g"
    CELLULAR_3G = "3g"
    ETHERNET = "ethernet"
    UNKNOWN = "unknown"


@dataclass
class EdgeDeviceConfig:
    """
    Configuration for an edge device.
    
    Attributes:
        device_id: Unique device identifier
        device_type: Type of device
        network_type: Network connection type
        bandwidth_mbps: Available bandwidth in Mbps
        cpu_cores: Number of CPU cores
        memory_mb: Available memory in MB
        storage_mb: Available storage in MB
        battery_powered: Whether device is battery powered
        battery_level: Battery level (0.0-1.0) if battery powered
        supports_hardware_decode: Whether device supports hardware decoding
        max_bitrate_kbps: Maximum supported bitrate in kbps
        metadata: Additional device metadata
    """
    
    device_id: str
    device_type: DeviceType
    network_type: NetworkType = NetworkType.UNKNOWN
    bandwidth_mbps: float = 10.0
    cpu_cores: int = 2
    memory_mb: int = 2048
    storage_mb: int = 1024
    battery_powered: bool = False
    battery_level: float = 1.0
    supports_hardware_decode: bool = True
    max_bitrate_kbps: int = 320
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not self.device_id:
            raise ValueError("device_id must be non-empty")
        
        if self.bandwidth_mbps < 0:
            raise ValueError("bandwidth_mbps must be non-negative")
        
        if self.cpu_cores < 1:
            raise ValueError("cpu_cores must be positive")
        
        if self.memory_mb < 0:
            raise ValueError("memory_mb must be non-negative")
        
        if self.storage_mb < 0:
            raise ValueError("storage_mb must be non-negative")
        
        if not 0.0 <= self.battery_level <= 1.0:
            raise ValueError("battery_level must be between 0.0 and 1.0")
        
        if self.max_bitrate_kbps < 0:
            raise ValueError("max_bitrate_kbps must be non-negative")
    
    def get_quality_tier(self) -> str:
        """
        Get recommended quality tier based on device capabilities.
        
        Returns:
            Quality tier: 'low', 'medium', 'high', or 'lossless'
        """
        # Consider bandwidth and device type
        if self.bandwidth_mbps >= 5.0 and self.device_type in [DeviceType.DESKTOP, DeviceType.LAPTOP]:
            return 'lossless'
        elif self.bandwidth_mbps >= 2.0:
            return 'high'
        elif self.bandwidth_mbps >= 1.0:
            return 'medium'
        else:
            return 'low'
    
    def should_use_cache(self) -> bool:
        """
        Determine if device should use aggressive caching.
        
        Returns:
            True if caching recommended, False otherwise
        """
        # Use cache if on cellular or limited bandwidth
        if self.network_type in [NetworkType.CELLULAR_3G, NetworkType.CELLULAR_4G]:
            return True
        
        if self.bandwidth_mbps < 2.0:
            return True
        
        # Use cache if battery powered and low battery
        if self.battery_powered and self.battery_level < 0.3:
            return True
        
        return False
    
    def get_buffer_size_seconds(self) -> int:
        """
        Get recommended buffer size in seconds.
        
        Returns:
            Buffer size in seconds
        """
        # Larger buffer for unstable connections
        if self.network_type == NetworkType.CELLULAR_3G:
            return 30
        elif self.network_type in [NetworkType.CELLULAR_4G, NetworkType.CELLULAR_5G]:
            return 15
        else:
            return 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'device_id': self.device_id,
            'device_type': self.device_type.value,
            'network_type': self.network_type.value,
            'bandwidth_mbps': self.bandwidth_mbps,
            'cpu_cores': self.cpu_cores,
            'memory_mb': self.memory_mb,
            'storage_mb': self.storage_mb,
            'battery_powered': self.battery_powered,
            'battery_level': self.battery_level,
            'supports_hardware_decode': self.supports_hardware_decode,
            'max_bitrate_kbps': self.max_bitrate_kbps,
            'metadata': self.metadata
        }
