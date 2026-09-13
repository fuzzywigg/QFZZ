"""EdgeOptimizer auto bandwidth_save via WIFI bandwidth < 1.0 Mbps."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def test_wifi_low_bandwidth_autosel_bandwidth_save():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="slow-wifi",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=0.5,
            storage_mb=2000,
            battery_powered=True,
            battery_level=0.8,  # above power_save threshold
        )
    )
    result = opt.optimize_streaming("slow-wifi")
    assert result["profile"] == "bandwidth_save"
