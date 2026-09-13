"""EdgeOptimizer bitrate bandwidth clamp and cache-via-profile edges."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def test_bitrate_clamped_to_eighty_percent_of_bandwidth():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="slow",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.CELLULAR_3G,
            bandwidth_mbps=0.1,
            storage_mb=2000,
            battery_powered=True,
            battery_level=0.8,
        )
    )
    result = opt.optimize_streaming(
        "slow",
        preferences={"profile": "quality", "quality": "high"},
    )
    # int(0.1 * 1024 * 0.8) == 81 — below quality-tier 256 / profile max 320
    assert result["bitrate_kbps"] == 81


def test_cache_disabled_when_profile_not_aggressive_and_device_skips_cache():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="desk",
            device_type=DeviceType.DESKTOP,
            network_type=NetworkType.ETHERNET,
            bandwidth_mbps=100.0,
            storage_mb=8000,
            battery_powered=False,
        )
    )
    # balanced: aggressive_cache=False; ethernet+high bw → should_use_cache False
    result = opt.optimize_streaming(
        "desk",
        preferences={"profile": "balanced", "quality": "high"},
    )
    assert result["cache_enabled"] is False
    assert result["cache_size_mb"] == 0
    assert result["preload_tracks"] == 0


def test_aggressive_cache_profile_sets_preload_count_five():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="cell",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.CELLULAR_4G,
            bandwidth_mbps=3.0,
            storage_mb=800,
            battery_powered=True,
            battery_level=0.9,
        )
    )
    result = opt.optimize_streaming(
        "cell",
        preferences={"profile": "power_save"},
    )
    assert result["cache_enabled"] is True
    assert result["preload_tracks"] == 5
    assert result["cache_size_mb"] == 100
