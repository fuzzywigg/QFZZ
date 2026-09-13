"""EdgeOptimizer non-desktop high bandwidth autosel stays balanced."""

from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType
from qfzz.edge.optimizer import EdgeOptimizer


def _opt_for(device_type: DeviceType, device_id: str) -> dict:
    opt = EdgeOptimizer()
    opt.register_device(
        EdgeDeviceConfig(
            device_id=device_id,
            device_type=device_type,
            network_type=NetworkType.WIFI,
            bandwidth_mbps=20.0,
            storage_mb=2000,
            battery_powered=False,
        )
    )
    return opt.optimize_streaming(device_id)


def test_iot_smart_speaker_car_high_bw_select_balanced_not_quality():
    for device_type, device_id in (
        (DeviceType.IOT, "iot1"),
        (DeviceType.SMART_SPEAKER, "spk1"),
        (DeviceType.CAR_SYSTEM, "car1"),
    ):
        result = _opt_for(device_type, device_id)
        assert result["profile"] == "balanced", device_type
