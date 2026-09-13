"""EdgeDeviceConfig.should_use_cache battery_level == 0.3 boundary (strict <)."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType


def test_battery_level_exactly_0_3_does_not_force_cache():
    cfg = EdgeDeviceConfig(
        device_id="batt-boundary",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=10.0,
        battery_powered=True,
        battery_level=0.3,
    )
    # Gate is battery_level < 0.3, so 0.3 must not enable cache on its own.
    assert cfg.should_use_cache() is False


def test_battery_level_just_below_0_3_forces_cache():
    cfg = EdgeDeviceConfig(
        device_id="batt-low",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=10.0,
        battery_powered=True,
        battery_level=0.299,
    )
    assert cfg.should_use_cache() is True
