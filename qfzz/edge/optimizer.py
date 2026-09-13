"""
Edge optimization for different device types.
"""

import logging
from typing import Any

from .config import DeviceType, EdgeDeviceConfig, NetworkType

logger = logging.getLogger(__name__)


class EdgeOptimizer:
    """
    Optimizes streaming parameters for different edge devices.

    Adjusts quality, buffering, and caching based on device capabilities
    and network conditions.
    """

    def __init__(self):
        """Initialize Edge Optimizer."""
        self._devices: dict[str, EdgeDeviceConfig] = {}
        self._optimization_profiles = self._init_optimization_profiles()
        logger.info("Edge Optimizer initialized")

    def _init_optimization_profiles(self) -> dict[str, dict[str, Any]]:
        """
        Initialize optimization profiles for different scenarios.

        Returns:
            Dictionary of optimization profiles
        """
        return {
            "power_save": {
                "max_quality": "medium",
                "buffer_multiplier": 1.5,
                "enable_hardware_decode": True,
                "aggressive_cache": True,
                "max_bitrate_kbps": 128,
            },
            "balanced": {
                "max_quality": "high",
                "buffer_multiplier": 1.0,
                "enable_hardware_decode": True,
                "aggressive_cache": False,
                "max_bitrate_kbps": 256,
            },
            "quality": {
                "max_quality": "lossless",
                "buffer_multiplier": 0.8,
                "enable_hardware_decode": True,
                "aggressive_cache": False,
                "max_bitrate_kbps": 320,
            },
            "bandwidth_save": {
                "max_quality": "low",
                "buffer_multiplier": 2.0,
                "enable_hardware_decode": True,
                "aggressive_cache": True,
                "max_bitrate_kbps": 96,
            },
        }

    def register_device(self, config: EdgeDeviceConfig) -> None:
        """
        Register a device for optimization.

        Args:
            config: Edge device configuration
        """
        self._devices[config.device_id] = config
        logger.info(f"Registered device: {config.device_id} ({config.device_type.value})")

    def unregister_device(self, device_id: str) -> bool:
        """
        Unregister a device.

        Args:
            device_id: Device identifier

        Returns:
            True if unregistered, False if not found
        """
        if device_id in self._devices:
            del self._devices[device_id]
            logger.info(f"Unregistered device: {device_id}")
            return True

        logger.warning(f"Device not found: {device_id}")
        return False

    def get_device_config(self, device_id: str) -> EdgeDeviceConfig | None:
        """
        Get device configuration.

        Args:
            device_id: Device identifier

        Returns:
            EdgeDeviceConfig if found, None otherwise
        """
        return self._devices.get(device_id)

    def optimize_streaming(
        self, device_id: str, preferences: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Get optimized streaming parameters for a device.

        Args:
            device_id: Device identifier
            preferences: Optional user preferences

        Returns:
            Dictionary of optimized streaming parameters
        """
        if device_id not in self._devices:
            raise ValueError(f"Device {device_id} not registered")

        device = self._devices[device_id]

        # Determine optimization profile
        profile_name = self._select_profile(device, preferences)
        profile = self._optimization_profiles[profile_name]

        # Calculate optimal parameters
        quality = self._calculate_quality(device, profile, preferences)
        bitrate = self._calculate_bitrate(device, profile, quality)
        buffer_size = self._calculate_buffer_size(device, profile)
        cache_settings = self._calculate_cache_settings(device, profile)

        optimization = {
            "device_id": device_id,
            "profile": profile_name,
            "quality": quality,
            "bitrate_kbps": bitrate,
            "buffer_size_seconds": buffer_size,
            "use_hardware_decode": device.supports_hardware_decode
            and profile["enable_hardware_decode"],
            "cache_enabled": cache_settings["enabled"],
            "cache_size_mb": cache_settings["size_mb"],
            "preload_tracks": cache_settings["preload_count"],
        }

        logger.debug(f"Optimized streaming for {device_id}: {quality} @ {bitrate}kbps")
        return optimization

    def _select_profile(
        self, device: EdgeDeviceConfig, preferences: dict[str, Any] | None
    ) -> str:
        """
        Select optimization profile based on device and preferences.

        Args:
            device: Device configuration
            preferences: Optional user preferences

        Returns:
            Profile name
        """
        # Check user preference
        if preferences and "profile" in preferences:
            profile = preferences["profile"]
            if profile in self._optimization_profiles:
                return profile

        # Auto-select based on device state
        if device.battery_powered and device.battery_level < 0.3:
            return "power_save"

        if device.network_type in [NetworkType.CELLULAR_3G, NetworkType.CELLULAR_4G]:
            return "bandwidth_save"

        if device.bandwidth_mbps < 1.0:
            return "bandwidth_save"

        if device.bandwidth_mbps >= 5.0 and device.device_type in [
            DeviceType.DESKTOP,
            DeviceType.LAPTOP,
        ]:
            return "quality"

        return "balanced"

    def _calculate_quality(
        self,
        device: EdgeDeviceConfig,
        profile: dict[str, Any],
        preferences: dict[str, Any] | None,
    ) -> str:
        """
        Calculate optimal quality setting.

        Args:
            device: Device configuration
            profile: Optimization profile
            preferences: Optional user preferences

        Returns:
            Quality tier
        """
        # Check user preference
        if preferences and "quality" in preferences:
            preferred = preferences["quality"]
            # Ensure it doesn't exceed device capability or profile max
            max_quality = profile["max_quality"]
            quality_order = ["low", "medium", "high", "lossless"]
            if quality_order.index(preferred) <= quality_order.index(max_quality):
                return preferred

        # Use device recommendation limited by profile
        device_quality = device.get_quality_tier()
        max_quality = profile["max_quality"]

        quality_order = ["low", "medium", "high", "lossless"]
        device_idx = quality_order.index(device_quality)
        max_idx = quality_order.index(max_quality)

        return quality_order[min(device_idx, max_idx)]

    def _calculate_bitrate(
        self, device: EdgeDeviceConfig, profile: dict[str, Any], quality: str
    ) -> int:
        """
        Calculate optimal bitrate.

        Args:
            device: Device configuration
            profile: Optimization profile
            quality: Quality tier

        Returns:
            Bitrate in kbps
        """
        # Base bitrates for quality tiers
        quality_bitrates = {"low": 96, "medium": 128, "high": 256, "lossless": 320}

        base_bitrate = quality_bitrates.get(quality, 128)

        # Limit by profile
        max_profile_bitrate = profile["max_bitrate_kbps"]

        # Limit by device
        max_device_bitrate = device.max_bitrate_kbps

        # Limit by bandwidth (use 80% of available bandwidth)
        bandwidth_limit_kbps = int(device.bandwidth_mbps * 1024 * 0.8)

        # Take minimum of all limits
        return min(base_bitrate, max_profile_bitrate, max_device_bitrate, bandwidth_limit_kbps)

    def _calculate_buffer_size(self, device: EdgeDeviceConfig, profile: dict[str, Any]) -> int:
        """
        Calculate optimal buffer size.

        Args:
            device: Device configuration
            profile: Optimization profile

        Returns:
            Buffer size in seconds
        """
        base_buffer = device.get_buffer_size_seconds()
        multiplier = profile["buffer_multiplier"]

        return int(base_buffer * multiplier)

    def _calculate_cache_settings(
        self, device: EdgeDeviceConfig, profile: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Calculate optimal cache settings.

        Args:
            device: Device configuration
            profile: Optimization profile

        Returns:
            Dictionary of cache settings
        """
        # Check if caching is recommended
        should_cache = profile["aggressive_cache"] or device.should_use_cache()

        if not should_cache:
            return {"enabled": False, "size_mb": 0, "preload_count": 0}

        # Calculate cache size based on available storage
        available_storage = device.storage_mb

        if available_storage < 100:
            cache_size = 0
            enabled = False
        elif available_storage < 500:
            cache_size = 50
            enabled = True
        elif available_storage < 1000:
            cache_size = 100
            enabled = True
        else:
            cache_size = 200
            enabled = True

        # Calculate preload count (3-5 tracks)
        preload_count = 5 if profile["aggressive_cache"] else 3

        return {"enabled": enabled, "size_mb": cache_size, "preload_count": preload_count}

    def update_network_conditions(
        self, device_id: str, network_type: NetworkType, bandwidth_mbps: float
    ) -> None:
        """
        Update network conditions for a device.

        Args:
            device_id: Device identifier
            network_type: Current network type
            bandwidth_mbps: Current bandwidth in Mbps
        """
        if device_id not in self._devices:
            raise ValueError(f"Device {device_id} not registered")

        device = self._devices[device_id]
        device.network_type = network_type
        device.bandwidth_mbps = bandwidth_mbps

        logger.info(
            f"Updated network for {device_id}: {network_type.value} @ {bandwidth_mbps} Mbps"
        )

    def update_battery_status(self, device_id: str, battery_level: float) -> None:
        """
        Update battery status for a device.

        Args:
            device_id: Device identifier
            battery_level: Battery level (0.0-1.0)
        """
        if device_id not in self._devices:
            raise ValueError(f"Device {device_id} not registered")

        device = self._devices[device_id]
        if not device.battery_powered:
            logger.warning(f"Device {device_id} is not battery powered")
            return

        # Clamp to valid range so later EdgeDeviceConfig.validate() stays consistent
        clamped = max(0.0, min(1.0, float(battery_level)))
        if clamped != battery_level:
            logger.warning(
                f"Battery level {battery_level} for {device_id} out of range; clamped to {clamped}"
            )
        device.battery_level = clamped
        logger.debug(f"Updated battery for {device_id}: {clamped:.1%}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get optimizer statistics.

        Returns:
            Dictionary of statistics
        """
        device_types = {}
        for device in self._devices.values():
            device_type = device.device_type.value
            device_types[device_type] = device_types.get(device_type, 0) + 1

        return {
            "total_devices": len(self._devices),
            "device_types": device_types,
            "available_profiles": list(self._optimization_profiles.keys()),
        }
