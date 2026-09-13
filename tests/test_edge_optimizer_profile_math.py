"""Cellular / cache / quality-clamp / battery no-op edges for EdgeOptimizer."""

import pytest

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def _device(**overrides) -> EdgeDeviceConfig:
    base = {
        "device_id": "edge-1",
        "device_type": DeviceType.SMARTPHONE,
        "network_type": NetworkType.WIFI,
        "bandwidth_mbps": 10.0,
        "storage_mb": 2000,
    }
    base.update(overrides)
    return EdgeDeviceConfig(**base)


def test_cellular_auto_profile_and_bad_preference():
    opt = EdgeOptimizer()
    opt.register_device(
        _device(network_type=NetworkType.CELLULAR_4G, bandwidth_mbps=3.0, battery_powered=True)
    )
    result = opt.optimize_streaming("edge-1", preferences={"profile": "not-a-real-profile"})
    assert result["profile"] == "bandwidth_save"


def test_quality_preference_clamped_to_profile_max():
    opt = EdgeOptimizer()
    opt.register_device(
        _device(
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.CELLULAR_3G,
            bandwidth_mbps=0.8,
            battery_powered=True,
            battery_level=0.5,
        )
    )
    result = opt.optimize_streaming(
        "edge-1",
        preferences={"profile": "bandwidth_save", "quality": "lossless"},
    )
    # bandwidth_save max_quality is low/medium — lossless must be clamped away
    assert result["quality"] != "lossless"
    assert result["quality"] in {"low", "medium"}


def test_storage_cache_tiers():
    opt = EdgeOptimizer()
    for storage, enabled, size in (
        (50, False, 0),
        (200, True, 50),
        (600, True, 100),
        (1500, True, 200),
    ):
        opt = EdgeOptimizer()
        opt.register_device(
            _device(
                device_id=f"s{storage}",
                storage_mb=storage,
                network_type=NetworkType.CELLULAR_4G,
                bandwidth_mbps=2.0,
            )
        )
        result = opt.optimize_streaming(f"s{storage}")
        assert result["cache_enabled"] is enabled
        assert result["cache_size_mb"] == size


def test_battery_update_desktop_noop_and_missing_device():
    opt = EdgeOptimizer()
    opt.register_device(
        _device(
            device_id="desk",
            device_type=DeviceType.DESKTOP,
            battery_powered=False,
            battery_level=1.0,
            network_type=NetworkType.ETHERNET,
        )
    )
    opt.update_battery_status("desk", 0.1)  # no-op for non-battery devices
    assert opt.get_device_config("desk").battery_level == 1.0
    with pytest.raises(ValueError, match="not registered"):
        opt.update_battery_status("ghost", 0.5)
    with pytest.raises(ValueError, match="not registered"):
        opt.update_network_conditions("ghost", NetworkType.WIFI, 5.0)
