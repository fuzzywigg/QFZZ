"""Tests for legacy edge.device_config dataclass."""

from qfzz.edge.device_config import EdgeDeviceConfig


def test_edge_device_config_defaults():
    cfg = EdgeDeviceConfig(device_id="d1", device_type="iot")
    assert cfg.device_id == "d1"
    assert cfg.max_memory_mb == 512
    assert cfg.max_model_size_mb == 100
    assert cfg.enable_6g is False
    assert cfg.network_bandwidth_mbps == 100
    assert cfg.storage_available_gb == 1.0


def test_edge_device_config_overrides():
    cfg = EdgeDeviceConfig(
        device_id="d2",
        device_type="phone",
        max_memory_mb=256,
        enable_6g=True,
        network_bandwidth_mbps=50,
    )
    assert cfg.max_memory_mb == 256
    assert cfg.enable_6g is True
    assert cfg.network_bandwidth_mbps == 50
