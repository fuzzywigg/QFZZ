"""Tests for edge device config and EdgeOptimizer."""

import pytest

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def _device(**overrides) -> EdgeDeviceConfig:
    base = {
        "device_id": "dev-1",
        "device_type": DeviceType.SMARTPHONE,
        "network_type": NetworkType.WIFI,
        "bandwidth_mbps": 10.0,
    }
    base.update(overrides)
    return EdgeDeviceConfig(**base)


class TestEdgeDeviceConfig:
    def test_validation(self):
        with pytest.raises(ValueError, match="device_id"):
            _device(device_id="")
        with pytest.raises(ValueError, match="bandwidth_mbps"):
            _device(bandwidth_mbps=-1)
        with pytest.raises(ValueError, match="cpu_cores"):
            _device(cpu_cores=0)
        with pytest.raises(ValueError, match="battery_level"):
            _device(battery_level=1.5)

    def test_quality_tier_and_buffer(self):
        desktop = _device(device_type=DeviceType.DESKTOP, bandwidth_mbps=6.0)
        assert desktop.get_quality_tier() == "lossless"
        low = _device(bandwidth_mbps=0.5)
        assert low.get_quality_tier() == "low"
        assert _device(network_type=NetworkType.CELLULAR_3G).get_buffer_size_seconds() == 30
        assert _device(network_type=NetworkType.WIFI).get_buffer_size_seconds() == 10

    def test_should_use_cache(self):
        assert _device(network_type=NetworkType.CELLULAR_4G).should_use_cache() is True
        assert _device(bandwidth_mbps=0.5).should_use_cache() is True
        phone = _device(battery_powered=True, battery_level=0.2)
        assert phone.should_use_cache() is True
        assert (
            _device(bandwidth_mbps=5.0, network_type=NetworkType.WIFI).should_use_cache() is False
        )

    def test_to_dict(self):
        data = _device().to_dict()
        assert data["device_type"] == "smartphone"
        assert data["network_type"] == "wifi"


class TestEdgeOptimizer:
    def test_register_unregister(self):
        opt = EdgeOptimizer()
        opt.register_device(_device())
        assert opt.get_device_config("dev-1") is not None
        assert opt.unregister_device("dev-1") is True
        assert opt.unregister_device("missing") is False

    def test_optimize_requires_registration(self):
        opt = EdgeOptimizer()
        with pytest.raises(ValueError, match="not registered"):
            opt.optimize_streaming("missing")

    def test_optimize_streaming_profiles(self):
        opt = EdgeOptimizer()
        opt.register_device(
            _device(
                device_type=DeviceType.DESKTOP,
                bandwidth_mbps=10.0,
                network_type=NetworkType.ETHERNET,
            )
        )
        result = opt.optimize_streaming("dev-1")
        assert result["profile"] == "quality"
        assert result["bitrate_kbps"] > 0
        assert "buffer_size_seconds" in result

        low_batt = _device(
            device_id="phone",
            battery_powered=True,
            battery_level=0.2,
            network_type=NetworkType.WIFI,
        )
        opt.register_device(low_batt)
        power = opt.optimize_streaming("phone")
        assert power["profile"] == "power_save"

        forced = opt.optimize_streaming("dev-1", preferences={"profile": "bandwidth_save"})
        assert forced["profile"] == "bandwidth_save"

    def test_update_network_and_battery(self):
        opt = EdgeOptimizer()
        opt.register_device(_device(battery_powered=True, battery_level=0.9))
        opt.update_network_conditions("dev-1", NetworkType.CELLULAR_3G, 0.8)
        cfg = opt.get_device_config("dev-1")
        assert cfg.network_type == NetworkType.CELLULAR_3G
        assert cfg.bandwidth_mbps == 0.8
        opt.update_battery_status("dev-1", 0.15)
        assert cfg.battery_level == 0.15
        with pytest.raises(ValueError):
            opt.update_network_conditions("missing", NetworkType.WIFI, 1.0)

    def test_statistics(self):
        opt = EdgeOptimizer()
        opt.register_device(_device())
        opt.register_device(_device(device_id="d2", device_type=DeviceType.LAPTOP))
        stats = opt.get_statistics()
        assert stats["total_devices"] == 2
        assert "balanced" in stats["available_profiles"]
