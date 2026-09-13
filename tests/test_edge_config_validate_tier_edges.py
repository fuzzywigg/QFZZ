"""Edge coverage for EdgeDeviceConfig validate, quality tiers, buffer, and cache."""

import pytest

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType


def _device(**overrides):
    base = {
        "device_id": "dev-1",
        "device_type": DeviceType.SMARTPHONE,
        "network_type": NetworkType.WIFI,
        "bandwidth_mbps": 5.0,
        "cpu_cores": 4,
        "memory_mb": 2048,
        "storage_mb": 1024,
        "max_bitrate_kbps": 320,
    }
    base.update(overrides)
    return EdgeDeviceConfig(**base)


def test_validate_negative_memory_storage_bitrate():
    with pytest.raises(ValueError, match="memory_mb"):
        _device(memory_mb=-1)
    with pytest.raises(ValueError, match="storage_mb"):
        _device(storage_mb=-1)
    with pytest.raises(ValueError, match="max_bitrate_kbps"):
        _device(max_bitrate_kbps=-1)


def test_quality_tiers_medium_high_lossless():
    assert _device(bandwidth_mbps=1.5).get_quality_tier() == "medium"
    assert _device(bandwidth_mbps=2.5, device_type=DeviceType.TABLET).get_quality_tier() == "high"
    assert (
        _device(bandwidth_mbps=6.0, device_type=DeviceType.LAPTOP).get_quality_tier() == "lossless"
    )
    assert _device(bandwidth_mbps=0.5).get_quality_tier() == "low"


def test_buffer_size_cellular_tiers():
    assert _device(network_type=NetworkType.CELLULAR_3G).get_buffer_size_seconds() == 30
    assert _device(network_type=NetworkType.CELLULAR_4G).get_buffer_size_seconds() == 15
    assert _device(network_type=NetworkType.CELLULAR_5G).get_buffer_size_seconds() == 15
    assert _device(network_type=NetworkType.ETHERNET).get_buffer_size_seconds() == 10


def test_should_use_cache_cellular_3g_and_battery():
    assert _device(network_type=NetworkType.CELLULAR_3G, bandwidth_mbps=10.0).should_use_cache()
    assert not _device(
        network_type=NetworkType.WIFI, bandwidth_mbps=10.0, battery_powered=False
    ).should_use_cache()
    assert _device(
        network_type=NetworkType.WIFI,
        bandwidth_mbps=10.0,
        battery_powered=True,
        battery_level=0.2,
    ).should_use_cache()


def test_to_dict_roundtrip_fields():
    d = _device(metadata={"os": "test"}).to_dict()
    assert d["device_id"] == "dev-1"
    assert d["device_type"] == "smartphone"
    assert d["metadata"]["os"] == "test"
