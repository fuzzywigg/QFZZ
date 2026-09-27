"""EdgeOptimizer auto-profile: wifi low-bw bandwidth_save and mid-tier balanced."""

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


def test_wifi_sub_megabit_selects_bandwidth_save_not_cellular():
    """bandwidth_mbps < 1.0 branch (must not be cellular / low-battery)."""
    opt = EdgeOptimizer()
    opt.register_device(
        _device(
            network_type=NetworkType.WIFI,
            bandwidth_mbps=0.4,
            battery_powered=True,
            battery_level=0.9,
        )
    )
    result = opt.optimize_streaming("edge-1")
    assert result["profile"] == "bandwidth_save"


def test_mid_bandwidth_phone_defaults_to_balanced():
    """Falls through to balanced when not power/cellular/low-bw/desktop-quality."""
    opt = EdgeOptimizer()
    opt.register_device(
        _device(
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=3.0,
            battery_powered=True,
            battery_level=0.7,
        )
    )
    result = opt.optimize_streaming("edge-1")
    assert result["profile"] == "balanced"
