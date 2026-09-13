"""EdgeDeviceConfig.should_use_cache bandwidth gate uses strict < 2.0."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType


def test_cache_bandwidth_exact_two_mbps_is_false_on_wifi():
    device = EdgeDeviceConfig(
        device_id="d1",
        device_type=DeviceType.LAPTOP,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=2.0,
        battery_powered=False,
    )
    assert device.should_use_cache() is False


def test_cache_bandwidth_just_below_two_mbps_is_true():
    device = EdgeDeviceConfig(
        device_id="d2",
        device_type=DeviceType.LAPTOP,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=1.999,
        battery_powered=False,
    )
    assert device.should_use_cache() is True
