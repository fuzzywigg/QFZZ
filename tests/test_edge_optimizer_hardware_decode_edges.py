"""EdgeOptimizer honors supports_hardware_decode=False."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def test_hardware_decode_disabled_when_device_lacks_support():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="soft",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=10.0,
            storage_mb=2000,
            battery_powered=True,
            battery_level=0.9,
            supports_hardware_decode=False,
        )
    )
    result = opt.optimize_streaming(
        "soft",
        preferences={"profile": "quality"},
    )
    assert result["use_hardware_decode"] is False
