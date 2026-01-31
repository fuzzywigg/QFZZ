# Core API

The core module provides the main station orchestrator and configuration.

## QFZZStation

::: qfzz.core.station.QFZZStation
    options:
      show_root_heading: true
      show_source: true

## StationConfig

::: qfzz.core.config.StationConfig
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from qfzz import QFZZStation, StationConfig

# Create configuration
config = StationConfig(
    station_name="My Station",
    edge_mode=True,
    blockchain_enabled=True
)

# Initialize and start station
station = QFZZStation(config)
station.initialize()
station.start()

# Get status
status = station.get_status()
print(status)

# Stop station
station.stop()
```
