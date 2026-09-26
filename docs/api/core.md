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

# Kwargs match live qfzz.core.config.StationConfig (no edge_mode=/blockchain_enabled=)
config = StationConfig(
    station_id="qfzz",
    station_name="My Station",
    enable_blockchain=True,
    enable_edge_optimization=True,
)

# Start station (no station.initialize() on tip)
station = QFZZStation(config)
station.start()

# Live stats accessor (no get_status() on tip)
stats = station.get_station_stats()
print(stats)

station.stop()
```
