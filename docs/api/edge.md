# Edge Computing API

The edge module optimizes QFZZ for edge device deployment.

## EdgeOptimizer

::: qfzz.edge.optimizer.EdgeOptimizer
    options:
      show_root_heading: true
      show_source: true

## EdgeDeviceConfig

::: qfzz.edge.config.EdgeDeviceConfig
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from qfzz import EdgeOptimizer
from qfzz.edge.config import DeviceType, EdgeDeviceConfig, NetworkType

# Kwargs match live qfzz.edge.config.EdgeDeviceConfig
# (not the orphan qfzz.edge.device_config schema; no max_memory_mb=/enable_6g=)
config = EdgeDeviceConfig(
    device_id="edge_001",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=10.0,
    memory_mb=512,
    battery_powered=True,
    battery_level=0.8,
)

# Live constructor takes no config arg; register devices after init
optimizer = EdgeOptimizer()
optimizer.register_device(config)

# Optimize streaming for a registered device_id
# (no optimize_model / add_to_cache / get_from_cache on tip)
streaming = optimizer.optimize_streaming("edge_001")
print(streaming)

stats = optimizer.get_statistics()
print(stats)
```
