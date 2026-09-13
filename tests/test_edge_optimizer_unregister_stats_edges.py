"""EdgeOptimizer unregister / empty stats / preferred-quality-accepted edges."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def _device(**overrides) -> EdgeDeviceConfig:
    base = {
        "device_id": "edge-1",
        "device_type": DeviceType.DESKTOP,
        "network_type": NetworkType.ETHERNET,
        "bandwidth_mbps": 20.0,
        "storage_mb": 2000,
    }
    base.update(overrides)
    return EdgeDeviceConfig(**base)


def test_unregister_miss_and_hit():
    opt = EdgeOptimizer()
    assert opt.unregister_device("missing") is False
    opt.register_device(_device())
    assert opt.unregister_device("edge-1") is True
    assert opt.get_device_config("edge-1") is None
    assert opt.unregister_device("edge-1") is False


def test_empty_statistics_and_available_profiles():
    opt = EdgeOptimizer()
    stats = opt.get_statistics()
    assert stats["total_devices"] == 0
    assert stats["device_types"] == {}
    assert set(stats["available_profiles"]) >= {
        "power_save",
        "balanced",
        "quality",
        "bandwidth_save",
    }


def test_preferred_quality_accepted_when_under_profile_max():
    opt = EdgeOptimizer()
    opt.register_device(_device())
    result = opt.optimize_streaming(
        "edge-1",
        preferences={"profile": "quality", "quality": "high"},
    )
    assert result["profile"] == "quality"
    assert result["quality"] == "high"


def test_laptop_autosel_quality_profile():
    opt = EdgeOptimizer()
    opt.register_device(
        _device(
            device_id="lap-1",
            device_type=DeviceType.LAPTOP,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=8.0,
            battery_powered=True,
            battery_level=0.8,
        )
    )
    result = opt.optimize_streaming("lap-1")
    assert result["profile"] == "quality"
