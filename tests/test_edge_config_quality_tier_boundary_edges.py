"""EdgeDeviceConfig.get_quality_tier exact bandwidth / device_type boundaries."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType


def _cfg(**kwargs) -> EdgeDeviceConfig:
    base = dict(
        device_id="tier-1",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=3.0,
    )
    base.update(kwargs)
    return EdgeDeviceConfig(**base)


def test_quality_tier_exact_bandwidth_thresholds():
    assert _cfg(bandwidth_mbps=2.0).get_quality_tier() == "high"
    assert _cfg(bandwidth_mbps=1.0).get_quality_tier() == "medium"
    assert _cfg(bandwidth_mbps=0.999).get_quality_tier() == "low"


def test_quality_tier_5mbps_non_desktop_stays_high():
    # lossless requires DESKTOP/LAPTOP AND bandwidth >= 5.0
    assert (
        _cfg(bandwidth_mbps=5.0, device_type=DeviceType.SMARTPHONE).get_quality_tier()
        == "high"
    )
    assert (
        _cfg(bandwidth_mbps=5.0, device_type=DeviceType.TABLET).get_quality_tier()
        == "high"
    )
    assert (
        _cfg(bandwidth_mbps=5.0, device_type=DeviceType.DESKTOP).get_quality_tier()
        == "lossless"
    )
