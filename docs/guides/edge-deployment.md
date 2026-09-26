# Edge Device Deployment Guide

> **Honesty:** Tip `qfzz/edge/` is a local streaming helper (`EdgeDeviceConfig` + `EdgeOptimizer`), not a shipping 6G / model-quantization / offline-cache product. Samples below match live `qfzz.edge.config.EdgeDeviceConfig` and `EdgeOptimizer()` — not the orphan `qfzz.edge.device_config` schema (`max_memory_mb` / `enable_6g` / `network_bandwidth_mbps` / …). See [Edge API](../api/edge.md).

## Table of Contents

1. [Overview](#overview)
2. [Supported device types](#supported-device-types)
3. [Register and optimize streaming](#register-and-optimize-streaming)
4. [Network and battery updates](#network-and-battery-updates)
5. [What tip does not ship](#what-tip-does-not-ship)

## Overview

The edge module adjusts streaming parameters from a registered device profile:

1. **`EdgeDeviceConfig`** — device id, type, network, memory, storage, battery fields
2. **`EdgeOptimizer`** — no-arg constructor; call `register_device(config)` then `optimize_streaming(device_id)`

```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer
from qfzz.edge.config import DeviceType, NetworkType

config = EdgeDeviceConfig(
    device_id="edge_001",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=10.0,
    memory_mb=512,
    battery_powered=True,
    battery_level=0.8,
)

optimizer = EdgeOptimizer()
optimizer.register_device(config)
streaming = optimizer.optimize_streaming("edge_001")
print(streaming)
# e.g. quality / bitrate_kbps / buffer_size_seconds / cache hints from tip profiles
```

Live public surface (tip): `register_device`, `unregister_device`, `optimize_streaming`, `update_network_conditions`, `update_battery_status`, `get_device_config`, `get_statistics`.

## Supported device types

`DeviceType` on tip: `smartphone`, `tablet`, `laptop`, `desktop`, `iot`, `smart_speaker`, `car_system`. There is no `embedded` enum member — use `DeviceType.IOT` for Pi-class hardware.

### Smartphone

```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer
from qfzz.edge.config import DeviceType, NetworkType

config = EdgeDeviceConfig(
    device_id="user_smartphone_001",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_5G,
    bandwidth_mbps=200.0,
    memory_mb=2048,
    storage_mb=8192,
    battery_powered=True,
    battery_level=0.9,
    max_bitrate_kbps=320,
)

optimizer = EdgeOptimizer()
optimizer.register_device(config)
print(optimizer.optimize_streaming("user_smartphone_001"))
```

### Smart speaker

```python
config = EdgeDeviceConfig(
    device_id="home_speaker_001",
    device_type=DeviceType.SMART_SPEAKER,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=100.0,
    memory_mb=512,
    storage_mb=2048,
    battery_powered=False,
    max_bitrate_kbps=256,
)

optimizer = EdgeOptimizer()
optimizer.register_device(config)
print(optimizer.optimize_streaming("home_speaker_001"))
```

### IoT / Pi-class

```python
config = EdgeDeviceConfig(
    device_id="embedded_rpi_001",
    device_type=DeviceType.IOT,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=50.0,
    memory_mb=256,
    storage_mb=1024,
    battery_powered=False,
    max_bitrate_kbps=128,
)

optimizer = EdgeOptimizer()
optimizer.register_device(config)
print(optimizer.optimize_streaming("embedded_rpi_001"))
```

## Register and optimize streaming

```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer
from qfzz.edge.config import DeviceType, NetworkType

optimizer = EdgeOptimizer()

config = EdgeDeviceConfig(
    device_id="edge_001",
    device_type=DeviceType.LAPTOP,
    network_type=NetworkType.ETHERNET,
    bandwidth_mbps=100.0,
    memory_mb=4096,
    storage_mb=16384,
)

optimizer.register_device(config)

# Optional preferences use tip keys profile=/quality= (not phantom bitrate_kbps=)
streaming = optimizer.optimize_streaming(
    "edge_001",
    preferences={"profile": "quality", "quality": "high"},
)
print(streaming["quality"], streaming["bitrate_kbps"], streaming["buffer_size_seconds"])

stats = optimizer.get_statistics()
print(stats)  # total_devices, device_types, available_profiles
```

`optimize_streaming(device_id)` raises `ValueError` if the device was never registered.

## Network and battery updates

```python
from qfzz.edge.config import NetworkType

optimizer.update_network_conditions(
    "edge_001",
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=5.0,
)
optimizer.update_battery_status("edge_001", battery_level=0.2)

# Re-run after conditions change
print(optimizer.optimize_streaming("edge_001"))
print(optimizer.get_device_config("edge_001"))
```

## What tip does not ship

Do **not** copy these from older guide drafts — they fail on tip:

| Phantom (orphan / aspirational) | Live tip |
| --- | --- |
| `EdgeDeviceConfig(..., max_memory_mb=, max_model_size_mb=, enable_6g=, network_bandwidth_mbps=, storage_available_gb=)` | `qfzz.edge.config.EdgeDeviceConfig` fields: `memory_mb`, `bandwidth_mbps`, `storage_mb`, `network_type`, … |
| `EdgeOptimizer(config)` | `EdgeOptimizer()` then `register_device(config)` |
| `optimize_streaming(bitrate_kbps=320)` | `optimize_streaming(device_id, preferences=None)` |
| `optimize_model` / `add_to_cache` / `get_from_cache` / `can_cache_locally` / `clear_cache` / `get_device_status` | Not on tip `EdgeOptimizer` |
| `device_type="embedded"` string / phantom 6G product mode | Use `DeviceType` enum; no `enable_6g` field |

Orphan module `qfzz.edge.device_config` still exists for legacy tests; exported tip path is `from qfzz.edge import EdgeDeviceConfig` → `qfzz.edge.config`.

For station wiring, use live `StationConfig(station_id=..., station_name=..., ...)` from [API core](../api/core.md) — tip has no `edge_mode=` / `enable_6g=` / `blockchain_enabled=` kwargs.
