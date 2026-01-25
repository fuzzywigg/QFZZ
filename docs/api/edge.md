# Edge Computing API

The edge module optimizes QFZZ for edge device deployment.

## EdgeOptimizer

::: qfzz.edge.optimizer.EdgeOptimizer
    options:
      show_root_heading: true
      show_source: true

## EdgeDeviceConfig

::: qfzz.edge.device_config.EdgeDeviceConfig
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from qfzz import EdgeOptimizer, EdgeDeviceConfig

# Configure device
config = EdgeDeviceConfig(
    device_id="edge_001",
    device_type="smartphone",
    max_memory_mb=512,
    max_model_size_mb=100,
    enable_6g=True,
    network_bandwidth_mbps=1000
)

# Create optimizer
optimizer = EdgeOptimizer(config)

# Optimize model
model_opt = optimizer.optimize_model(250.0)
print(model_opt)

# Optimize streaming
streaming_config = optimizer.optimize_streaming(320)
print(streaming_config)

# Cache data
optimizer.add_to_cache("track_001", {"title": "Test"}, 5.0)
data = optimizer.get_from_cache("track_001")
```
