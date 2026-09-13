"""Edge config validation, quality tiers, buffer, and cache branches."""

import pytest

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType


def _cfg(**kwargs) -> EdgeDeviceConfig:
    base = dict(
        device_id="dev-1",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=3.0,
    )
    base.update(kwargs)
    return EdgeDeviceConfig(**base)


def test_validate_negative_memory_storage_bitrate():
    with pytest.raises(ValueError, match="memory_mb"):
        _cfg(memory_mb=-1)
    with pytest.raises(ValueError, match="storage_mb"):
        _cfg(storage_mb=-1)
    with pytest.raises(ValueError, match="max_bitrate"):
        _cfg(max_bitrate_kbps=-1)


def test_quality_tier_medium_high_lossless():
    assert _cfg(bandwidth_mbps=1.5, device_type=DeviceType.SMARTPHONE).get_quality_tier() == "medium"
    assert _cfg(bandwidth_mbps=2.5, device_type=DeviceType.TABLET).get_quality_tier() == "high"
    assert _cfg(bandwidth_mbps=5.0, device_type=DeviceType.LAPTOP).get_quality_tier() == "lossless"
    assert _cfg(bandwidth_mbps=0.5).get_quality_tier() == "low"


def test_buffer_size_for_cellular():
    assert _cfg(network_type=NetworkType.CELLULAR_3G).get_buffer_size_seconds() == 30
    assert _cfg(network_type=NetworkType.CELLULAR_4G).get_buffer_size_seconds() == 15
    assert _cfg(network_type=NetworkType.CELLULAR_5G).get_buffer_size_seconds() == 15
    assert _cfg(network_type=NetworkType.WIFI).get_buffer_size_seconds() == 10


def test_should_use_cache_cellular5g_alone_false():
    # CELLULAR_5G is intentionally not in the cellular cache list
    cfg = _cfg(network_type=NetworkType.CELLULAR_5G, bandwidth_mbps=10.0, battery_powered=False)
    assert cfg.should_use_cache() is False

    assert _cfg(network_type=NetworkType.CELLULAR_4G, bandwidth_mbps=10.0).should_use_cache() is True
    assert _cfg(bandwidth_mbps=1.0).should_use_cache() is True
    low_batt = _cfg(
        network_type=NetworkType.WIFI,
        bandwidth_mbps=10.0,
        battery_powered=True,
        battery_level=0.2,
    )
    assert low_batt.should_use_cache() is True
