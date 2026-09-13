"""Balanced profile with cache-on yields preload_count=3 (not aggressive 5)."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def test_balanced_profile_preload_three_when_caching():
    opt = EdgeOptimizer()
    # Cellular ⇒ should_use_cache True; explicit balanced ⇒ aggressive_cache False
    opt.register_device(
        EdgeDeviceConfig(
            device_id="cell-bal",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.CELLULAR_4G,
            bandwidth_mbps=3.0,
            storage_mb=800,
            battery_powered=True,
            battery_level=0.9,
        )
    )
    result = opt.optimize_streaming(
        "cell-bal",
        preferences={"profile": "balanced"},
    )
    assert result["cache_enabled"] is True
    assert result["preload_tracks"] == 3
    assert result["profile"] == "balanced"
