"""EdgeOptimizer clamps out-of-range battery levels."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def test_update_battery_status_clamps_high_and_low():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="phone",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=10.0,
            battery_powered=True,
            battery_level=0.8,
        )
    )
    opt.update_battery_status("phone", 1.5)
    assert opt.get_device_config("phone").battery_level == 1.0
    opt.get_device_config("phone").validate()

    opt.update_battery_status("phone", -0.25)
    assert opt.get_device_config("phone").battery_level == 0.0
    opt.get_device_config("phone").validate()


def test_update_battery_status_accepts_inclusive_bounds():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="phone",
            device_type=DeviceType.SMARTPHONE,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=10.0,
            battery_powered=True,
            battery_level=0.5,
        )
    )
    opt.update_battery_status("phone", 0.0)
    assert opt.get_device_config("phone").battery_level == 0.0
    opt.update_battery_status("phone", 1.0)
    assert opt.get_device_config("phone").battery_level == 1.0
