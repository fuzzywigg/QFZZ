"""EdgeOptimizer accepts in-range preferred quality without clamping away."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def test_quality_preference_accepted_when_within_profile_max():
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id="desk",
            device_type=DeviceType.DESKTOP,
            network_type=NetworkType.ETHERNET,
            bandwidth_mbps=100.0,
            storage_mb=8000,
            battery_powered=False,
        )
    )
    # balanced / high-tier desktop profiles allow high; prefer medium explicitly
    result = opt.optimize_streaming(
        "desk",
        preferences={"profile": "balanced", "quality": "medium"},
    )
    assert result["quality"] == "medium"
    assert result["profile"] == "balanced"
