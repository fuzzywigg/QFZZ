# QFZZ Configuration Guide

Complete reference for configuring QFZZ stations and edge devices, including StationConfig, EdgeDeviceConfig, environment variables, best practices, and performance tuning.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [StationConfig Reference](#stationconfig-reference)
- [EdgeDeviceConfig Reference](#edgedeviceconfig-reference)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Best Practices](#best-practices)
- [Security Considerations](#security-considerations)
- [Performance Tuning](#performance-tuning)
- [Advanced Configuration](#advanced-configuration)
- [Configuration Examples](#configuration-examples)

## Configuration Overview

QFZZ uses a hierarchical configuration system:

1. **Default Values** - Built-in defaults in code
2. **Configuration Files** - JSON/YAML files override defaults
3. **Environment Variables** - Environment variables override files
4. **Runtime Configuration** - Python objects override all

### Configuration Priority (highest to lowest)

```
Runtime Configuration (Python objects)
        ↓
Environment Variables
        ↓
Configuration Files (JSON/YAML)
        ↓
Default Values
```

## StationConfig Reference

### StationConfig Class

The `StationConfig` class defines all station-level settings.

#### Basic Usage

```python
from qfzz.core.config import StationConfig

# Create basic configuration
config = StationConfig(
    station_id="my_station_001",
    station_name="My QFZZ Station"
)

# Create detailed configuration
config = StationConfig(
    station_id="my_station_001",
    station_name="My QFZZ Station",
    max_playlist_size=50,
    trust_threshold=0.7,
    enable_blockchain=True,
    enable_edge_optimization=True,
    streaming_quality="high",
    allowed_licenses=["CC-BY", "CC-BY-SA", "CC0"],
    cache_size_mb=1000,
    metadata={
        "region": "US-West",
        "tier": "premium",
        "created_by": "admin"
    }
)
```

### Configuration Parameters

#### Required Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `station_id` | str | Unique identifier for station | **Required** |
| `station_name` | str | Human-readable station name | **Required** |

#### Feature Toggle Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `enable_blockchain` | bool | Enable blockchain trust network | True |
| `enable_edge_optimization` | bool | Enable edge device optimization | True |

#### Playlist Parameters

| Parameter | Type | Range | Description | Default |
|-----------|------|-------|-------------|---------|
| `max_playlist_size` | int | 1-10000 | Maximum tracks per playlist | 100 |
| `trust_threshold` | float | 0.0-1.0 | Minimum trust score for content | 0.6 |

#### Quality Parameters

| Parameter | Type | Options | Description | Default |
|-----------|------|---------|-------------|---------|
| `streaming_quality` | str | low, medium, high, lossless | Default streaming quality | high |
| `cache_size_mb` | int | 0+ | Cache size in megabytes | 500 |

#### Content Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `allowed_licenses` | List[str] | Acceptable content licenses | ['CC-BY', 'CC-BY-SA', 'CC0'] |
| `metadata` | Dict | Custom metadata | {} |

### Detailed Parameter Descriptions

#### station_id
- **Type**: `str`
- **Required**: Yes
- **Validation**: Non-empty string
- **Example**: "station_001", "user_alice_station"
- **Notes**: Used as unique identifier across system

```python
config = StationConfig(
    station_id="user_alice_station",
    station_name="Alice's Station"
)
```

#### station_name
- **Type**: `str`
- **Required**: Yes
- **Validation**: Non-empty string
- **Example**: "Alice's Indie Mix", "Rock Enthusiast's Station"
- **Notes**: User-facing name, displayed in UI

```python
config = StationConfig(
    station_id="station_001",
    station_name="Electronic Dance Music Station"
)
```

#### max_playlist_size
- **Type**: `int`
- **Range**: 1 to 10,000
- **Default**: 100
- **Notes**: Affects memory usage and UI performance

```python
# Small playlists (mobile devices)
config = StationConfig(
    station_id="s1",
    station_name="Mobile Station",
    max_playlist_size=20
)

# Large playlists (desktop/streaming)
config = StationConfig(
    station_id="s1",
    station_name="Desktop Station",
    max_playlist_size=500
)
```

#### trust_threshold
- **Type**: `float`
- **Range**: 0.0 - 1.0
- **Default**: 0.6
- **Meaning**:
  - 0.0 = Accept all content
  - 0.5 = Balanced approach
  - 0.9 = Only highly trusted content

```python
# Conservative (only trusted content)
config = StationConfig(
    station_id="s1",
    station_name="Trusted Content Only",
    trust_threshold=0.8
)

# Permissive (allows experimental content)
config = StationConfig(
    station_id="s1",
    station_name="Discovery Station",
    trust_threshold=0.3
)
```

#### enable_blockchain
- **Type**: `bool`
- **Default**: True
- **Effect**: Controls blockchain trust network functionality

```python
# Enable blockchain for content verification
config = StationConfig(
    station_id="s1",
    station_name="Secure Station",
    enable_blockchain=True  # Slower but more secure
)

# Disable for faster operation
config = StationConfig(
    station_id="s1",
    station_name="Fast Station",
    enable_blockchain=False  # Faster but less secure
)
```

#### enable_edge_optimization
- **Type**: `bool`
- **Default**: True
- **Effect**: Controls device-aware optimization

```python
# Enable for multi-device support
config = StationConfig(
    station_id="s1",
    station_name="Multi-Device Station",
    enable_edge_optimization=True
)
```

#### streaming_quality
- **Type**: `str`
- **Options**: `low`, `medium`, `high`, `lossless`
- **Default**: `high`
- **Bandwidth Requirements**:
  - `low`: 64-128 kbps (2G networks)
  - `medium`: 192-256 kbps (3G networks)
  - `high`: 320 kbps (4G/WiFi)
  - `lossless`: 1-2 Mbps (high-bandwidth)

```python
# Mobile-optimized (low bandwidth)
config = StationConfig(
    station_id="s1",
    station_name="Mobile Station",
    streaming_quality="medium"
)

# Desktop/audiophile (high bandwidth)
config = StationConfig(
    station_id="s1",
    station_name="Audiophile Station",
    streaming_quality="lossless"
)
```

#### allowed_licenses
- **Type**: `List[str]`
- **Default**: `['CC-BY', 'CC-BY-SA', 'CC0']`
- **Common Licenses**:
  - `CC0`: Public domain
  - `CC-BY`: Attribution required
  - `CC-BY-SA`: Attribution + Share-Alike
  - `CC-BY-NC`: Non-commercial
  - `ALL-RIGHTS-RESERVED`: Proprietary

```python
# Only public domain and CC-BY
config = StationConfig(
    station_id="s1",
    station_name="Open Station",
    allowed_licenses=["CC0", "CC-BY"]
)

# Allow non-commercial use
config = StationConfig(
    station_id="s1",
    station_name="Non-Profit Station",
    allowed_licenses=["CC0", "CC-BY", "CC-BY-NC"]
)
```

#### cache_size_mb
- **Type**: `int`
- **Range**: 0+
- **Default**: 500 MB
- **Notes**: Set to 0 to disable caching

```python
# Large cache for offline listening
config = StationConfig(
    station_id="s1",
    station_name="Offline Station",
    cache_size_mb=2000
)

# No cache for memory-constrained devices
config = StationConfig(
    station_id="s1",
    station_name="Minimal Station",
    cache_size_mb=0
)
```

#### metadata
- **Type**: `Dict[str, Any]`
- **Default**: `{}`
- **Notes**: Custom key-value pairs for application use

```python
config = StationConfig(
    station_id="s1",
    station_name="Custom Station",
    metadata={
        "owner_id": "user_123",
        "region": "us-west-1",
        "tier": "premium",
        "created_at": "2024-01-01",
        "tags": ["rock", "indie", "alternative"]
    }
)

# Access metadata
owner = config.metadata.get("owner_id")
region = config.metadata.get("region")
```

### Configuration Methods

#### Converting to Dictionary

```python
config = StationConfig(station_id="s1", station_name="My Station")

# Convert to dictionary
config_dict = config.to_dict()
print(config_dict)
# {
#     'station_id': 's1',
#     'station_name': 'My Station',
#     'max_playlist_size': 100,
#     ...
# }
```

#### Converting to JSON

```python
# Convert to JSON string
json_str = config.to_json()
print(json_str)
# {
#   "station_id": "s1",
#   "station_name": "My Station",
#   ...
# }

# Save to file
with open("station_config.json", "w") as f:
    f.write(config.to_json())
```

#### Creating from Dictionary

```python
config_data = {
    "station_id": "s1",
    "station_name": "My Station",
    "max_playlist_size": 50,
    "trust_threshold": 0.7
}

config = StationConfig.from_dict(config_data)
```

#### Creating from JSON

```python
json_str = '''
{
    "station_id": "s1",
    "station_name": "My Station",
    "max_playlist_size": 50
}
'''

config = StationConfig.from_json(json_str)

# Or from file
with open("station_config.json", "r") as f:
    config = StationConfig.from_json(f.read())
```

## EdgeDeviceConfig Reference

### EdgeDeviceConfig Class

Configuration for edge devices (phones, tablets, etc.)

#### Basic Usage

```python
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

# Smartphone on WiFi
config = EdgeDeviceConfig(
    device_id="phone_001",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=5.0,
    cpu_cores=4,
    memory_mb=4096,
    battery_powered=True,
    battery_level=0.8
)

# Desktop on Ethernet
config = EdgeDeviceConfig(
    device_id="desktop_001",
    device_type=DeviceType.DESKTOP,
    network_type=NetworkType.ETHERNET,
    bandwidth_mbps=100.0,
    cpu_cores=8,
    memory_mb=16384,
    battery_powered=False
)
```

### Device Types

| Type | Description | Use Case |
|------|-------------|----------|
| `SMARTPHONE` | Mobile phone | On-the-go listening |
| `TABLET` | Tablet device | Portable home use |
| `LAPTOP` | Laptop computer | Mobile work |
| `DESKTOP` | Desktop computer | Stationary work/listening |
| `IOT` | IoT device | Smart speakers, displays |
| `SMART_SPEAKER` | Smart speaker | Alexa, Google Home |
| `CAR_SYSTEM` | Car audio system | In-vehicle listening |

### Network Types

| Type | Bandwidth | Latency | Reliability |
|------|-----------|---------|-------------|
| `ETHERNET` | 1-10 Gbps | <5ms | Very high |
| `WIFI` | 5-100 Mbps | 20-50ms | High |
| `CELLULAR_5G` | 100 Mbps - 1 Gbps | 1-20ms | Good |
| `CELLULAR_4G` | 5-50 Mbps | 50-100ms | Good |
| `CELLULAR_3G` | 0.5-3 Mbps | 100-500ms | Moderate |
| `UNKNOWN` | Unknown | Unknown | Unknown |

### Configuration Parameters

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | str | Unique device identifier |
| `device_type` | DeviceType | Type of device |

#### Optional Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `network_type` | NetworkType | UNKNOWN | - | Network connection type |
| `bandwidth_mbps` | float | 10.0 | 0+ | Available bandwidth |
| `cpu_cores` | int | 2 | 1+ | Number of CPU cores |
| `memory_mb` | int | 2048 | 0+ | Available memory in MB |
| `storage_mb` | int | 1024 | 0+ | Available storage in MB |
| `battery_powered` | bool | False | - | Whether device is battery powered |
| `battery_level` | float | 1.0 | 0.0-1.0 | Battery level (if battery powered) |
| `supports_hardware_decode` | bool | True | - | Hardware decoding support |
| `max_bitrate_kbps` | int | 320 | 0+ | Maximum bitrate supported |
| `metadata` | Dict | {} | - | Custom metadata |

### Device Configuration Examples

#### High-End Smartphone

```python
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

config = EdgeDeviceConfig(
    device_id="iphone_14_pro",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_5G,
    bandwidth_mbps=50.0,
    cpu_cores=6,
    memory_mb=6144,
    storage_mb=128000,
    battery_powered=True,
    battery_level=0.9,
    supports_hardware_decode=True,
    max_bitrate_kbps=320,
    metadata={
        "model": "iPhone 14 Pro",
        "os": "iOS 17"
    }
)
```

#### Budget Smartphone on Cellular

```python
config = EdgeDeviceConfig(
    device_id="budget_phone",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=2.0,
    cpu_cores=4,
    memory_mb=2048,
    storage_mb=16000,
    battery_powered=True,
    battery_level=0.3,
    supports_hardware_decode=False,
    max_bitrate_kbps=128,
    metadata={"model": "Budget Model"}
)
```

#### Desktop Computer

```python
config = EdgeDeviceConfig(
    device_id="workstation",
    device_type=DeviceType.DESKTOP,
    network_type=NetworkType.ETHERNET,
    bandwidth_mbps=1000.0,
    cpu_cores=16,
    memory_mb=32768,
    storage_mb=2000000,
    battery_powered=False,
    supports_hardware_decode=True,
    max_bitrate_kbps=1411,  # FLAC bitrate
    metadata={"model": "High-end Workstation"}
)
```

#### Smart Speaker

```python
config = EdgeDeviceConfig(
    device_id="smart_speaker_001",
    device_type=DeviceType.SMART_SPEAKER,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=10.0,
    cpu_cores=2,
    memory_mb=1024,
    storage_mb=8000,
    battery_powered=False,
    supports_hardware_decode=True,
    max_bitrate_kbps=256,
    metadata={"model": "Amazon Echo"}
)
```

### Device Helper Methods

#### get_quality_tier()

Returns recommended quality tier based on device capabilities:

```python
device = EdgeDeviceConfig(
    device_id="phone",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=5.0
)

quality = device.get_quality_tier()
print(quality)  # Output: "high"
```

**Quality Tier Logic**:
- `lossless`: Desktop/Laptop with ≥5 Mbps
- `high`: ≥2 Mbps
- `medium`: ≥1 Mbps
- `low`: <1 Mbps

#### should_use_cache()

Determines if device should use aggressive caching:

```python
device = EdgeDeviceConfig(
    device_id="phone",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_3G,
    bandwidth_mbps=1.0,
    battery_powered=True,
    battery_level=0.2
)

use_cache = device.should_use_cache()
print(use_cache)  # Output: True
```

**Caching is enabled for**:
- 3G/4G networks
- Bandwidth <2 Mbps
- Battery powered devices with <30% battery

#### get_buffer_size_seconds()

Returns recommended buffer size in seconds:

```python
device = EdgeDeviceConfig(
    device_id="phone",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_3G
)

buffer_size = device.get_buffer_size_seconds()
print(buffer_size)  # Output: 30
```

**Buffer Sizes**:
- 3G: 30 seconds
- 4G/5G: 15 seconds
- WiFi/Ethernet: 10 seconds

## Configuration Files

### JSON Configuration File

Create `station_config.json`:

```json
{
  "station_id": "my_station",
  "station_name": "My QFZZ Station",
  "max_playlist_size": 100,
  "trust_threshold": 0.6,
  "enable_blockchain": true,
  "enable_edge_optimization": true,
  "streaming_quality": "high",
  "allowed_licenses": [
    "CC-BY",
    "CC-BY-SA",
    "CC0"
  ],
  "cache_size_mb": 500,
  "metadata": {
    "region": "us-west",
    "tier": "premium"
  }
}
```

Load configuration from file:

```python
import json
from qfzz.core.config import StationConfig

# Read JSON file
with open("station_config.json", "r") as f:
    config = StationConfig.from_json(f.read())
```

### YAML Configuration File

Create `station_config.yaml`:

```yaml
station_id: my_station
station_name: My QFZZ Station
max_playlist_size: 100
trust_threshold: 0.6
enable_blockchain: true
enable_edge_optimization: true
streaming_quality: high
allowed_licenses:
  - CC-BY
  - CC-BY-SA
  - CC0
cache_size_mb: 500
metadata:
  region: us-west
  tier: premium
```

Load YAML configuration:

```python
import yaml
from qfzz.core.config import StationConfig

# Read YAML file
with open("station_config.yaml", "r") as f:
    config_data = yaml.safe_load(f)
    config = StationConfig.from_dict(config_data)
```

### Configuration Directory Structure

```
my-qfzz-app/
├── config/
│   ├── station_config.json
│   ├── devices/
│   │   ├── phone.json
│   │   ├── desktop.json
│   │   └── tablet.json
│   └── environments/
│       ├── development.json
│       ├── staging.json
│       └── production.json
├── app.py
└── main.py
```

## Environment Variables

### Station Configuration

Environment variables with `QFZZ_STATION_` prefix:

```bash
# Basic settings
export QFZZ_STATION_ID=my_station
export QFZZ_STATION_NAME="My QFZZ Station"

# Playlist settings
export QFZZ_STATION_MAX_PLAYLIST_SIZE=100
export QFZZ_STATION_TRUST_THRESHOLD=0.6

# Feature toggles
export QFZZ_STATION_ENABLE_BLOCKCHAIN=true
export QFZZ_STATION_ENABLE_EDGE_OPTIMIZATION=true

# Quality settings
export QFZZ_STATION_STREAMING_QUALITY=high
export QFZZ_STATION_CACHE_SIZE_MB=500

# Licensing
export QFZZ_STATION_ALLOWED_LICENSES=CC-BY,CC-BY-SA,CC0
```

### Device Configuration

Environment variables with `QFZZ_DEVICE_` prefix:

```bash
# Device identification
export QFZZ_DEVICE_ID=phone_001
export QFZZ_DEVICE_TYPE=smartphone
export QFZZ_DEVICE_NETWORK_TYPE=wifi

# Device capabilities
export QFZZ_DEVICE_BANDWIDTH_MBPS=5.0
export QFZZ_DEVICE_CPU_CORES=4
export QFZZ_DEVICE_MEMORY_MB=4096
export QFZZ_DEVICE_STORAGE_MB=128000

# Battery settings
export QFZZ_DEVICE_BATTERY_POWERED=true
export QFZZ_DEVICE_BATTERY_LEVEL=0.8

# Audio settings
export QFZZ_DEVICE_SUPPORTS_HARDWARE_DECODE=true
export QFZZ_DEVICE_MAX_BITRATE_KBPS=320
```

### Application Settings

```bash
# Logging
export QFZZ_LOG_LEVEL=INFO
export QFZZ_LOG_FILE=qfzz.log

# Performance
export QFZZ_WORKER_THREADS=4
export QFZZ_MAX_CONNECTIONS=100

# Security
export QFZZ_ENABLE_SSL=true
export QFZZ_SSL_CERT_PATH=/path/to/cert.pem
```

### Reading Environment Variables in Python

```python
import os
from qfzz.core.config import StationConfig

# Method 1: Direct environment variables
station_id = os.getenv("QFZZ_STATION_ID", "default_station")
station_name = os.getenv("QFZZ_STATION_NAME", "Default Station")

config = StationConfig(
    station_id=station_id,
    station_name=station_name,
    max_playlist_size=int(os.getenv("QFZZ_STATION_MAX_PLAYLIST_SIZE", "100")),
    enable_blockchain=os.getenv("QFZZ_STATION_ENABLE_BLOCKCHAIN", "true").lower() == "true"
)

# Method 2: Using python-dotenv
from dotenv import load_dotenv

load_dotenv()  # Load from .env file
config = StationConfig(
    station_id=os.getenv("QFZZ_STATION_ID"),
    station_name=os.getenv("QFZZ_STATION_NAME")
)
```

### .env File

Create `.env` file for local development:

```bash
# .env
QFZZ_STATION_ID=dev_station
QFZZ_STATION_NAME=Development Station
QFZZ_STATION_ENABLE_BLOCKCHAIN=false
QFZZ_STATION_CACHE_SIZE_MB=100
QFZZ_LOG_LEVEL=DEBUG
```

## Best Practices

### Configuration Validation

Always validate configuration before using:

```python
from qfzz.core.config import StationConfig

try:
    config = StationConfig(
        station_id="my_station",
        station_name="My Station",
        trust_threshold=0.7  # Valid: 0-1
    )
    # Validation occurs in __post_init__
    print("✓ Configuration is valid")
except ValueError as e:
    print(f"✗ Configuration error: {e}")
```

### Configuration Versioning

Track configuration changes:

```python
config_v1 = {
    "version": "1.0",
    "station_id": "station_001",
    "station_name": "My Station"
}

config_v2 = {
    "version": "2.0",
    "station_id": "station_001",
    "station_name": "My Upgraded Station",
    "cache_size_mb": 1000  # New in v2
}
```

### Configuration Inheritance

Create base configurations:

```python
from qfzz.core.config import StationConfig

# Base configuration
BASE_CONFIG = {
    "enable_blockchain": True,
    "enable_edge_optimization": True,
    "allowed_licenses": ["CC-BY", "CC-BY-SA", "CC0"],
    "cache_size_mb": 500
}

# Development overrides
DEV_CONFIG = {
    **BASE_CONFIG,
    "station_id": "dev_station",
    "station_name": "Development Station",
    "trust_threshold": 0.3,  # More permissive
    "streaming_quality": "low"  # Lower bandwidth
}

# Production overrides
PROD_CONFIG = {
    **BASE_CONFIG,
    "station_id": "prod_station",
    "station_name": "Production Station",
    "trust_threshold": 0.8,  # More restrictive
    "streaming_quality": "high",
    "cache_size_mb": 2000
}

dev_config = StationConfig(**DEV_CONFIG)
prod_config = StationConfig(**PROD_CONFIG)
```

### Environment-Specific Configuration

```python
import os
from qfzz.core.config import StationConfig

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

CONFIGS = {
    "development": {
        "station_id": "dev_station",
        "station_name": "Dev Station",
        "trust_threshold": 0.3,
        "enable_blockchain": False
    },
    "staging": {
        "station_id": "staging_station",
        "station_name": "Staging Station",
        "trust_threshold": 0.6,
        "enable_blockchain": True
    },
    "production": {
        "station_id": "prod_station",
        "station_name": "Production Station",
        "trust_threshold": 0.8,
        "enable_blockchain": True
    }
}

config_dict = CONFIGS.get(ENVIRONMENT, CONFIGS["development"])
config = StationConfig(**config_dict)
```

## Security Considerations

### Sensitive Configuration Data

!!! warning "Protect Sensitive Data"
    Never commit sensitive data (API keys, credentials) to version control.

```bash
# .gitignore
.env
.env.local
secrets/
config/credentials.json
config/private_keys/
```

### Secure Configuration Management

Use environment variables for sensitive data:

```python
import os
from qfzz.core.config import StationConfig

# Secure way: Use environment variables
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")

# Insecure way: Hardcoded (NEVER DO THIS)
# FIREBASE_API_KEY = "abc123def456"  # ✗ WRONG!
```

### Configuration File Permissions

Restrict file permissions for config files containing secrets:

```bash
# On Linux/macOS
chmod 600 config/private_config.json  # Only owner can read
chmod 600 .env                        # Only owner can read

# Verify permissions
ls -l config/
```

### SSL/TLS Configuration

For production deployments:

```python
config = StationConfig(
    station_id="prod_station",
    station_name="Production Station",
    metadata={
        "use_ssl": True,
        "ssl_cert_path": "/etc/ssl/certs/qfzz.crt",
        "ssl_key_path": "/etc/ssl/private/qfzz.key"
    }
)
```

## Performance Tuning

### Playlist Size Optimization

```python
# Small playlists (memory-efficient)
config = StationConfig(
    station_id="s1",
    station_name="Mobile Station",
    max_playlist_size=20  # Low memory usage
)

# Large playlists (better discovery)
config = StationConfig(
    station_id="s1",
    station_name="Exploration Station",
    max_playlist_size=500  # More options, more memory
)
```

**Guidelines**:
- Mobile devices: 20-50 tracks
- Tablets: 50-200 tracks
- Desktops: 200-1000 tracks

### Cache Optimization

```python
# Aggressive caching (faster, more storage)
config = StationConfig(
    station_id="s1",
    station_name="Cached Station",
    cache_size_mb=2000
)

# Minimal caching (slower, less storage)
config = StationConfig(
    station_id="s1",
    station_name="Minimal Station",
    cache_size_mb=100
)
```

**Cache Size Guidelines**:
- Low-bandwidth networks: 500-1000 MB
- High-bandwidth networks: 100-500 MB
- Memory-constrained: 50-100 MB
- Storage-rich devices: 1000-5000 MB

### Blockchain Trade-offs

```python
# With blockchain (more secure, slower)
config_secure = StationConfig(
    station_id="s1",
    station_name="Secure Station",
    enable_blockchain=True
)

# Without blockchain (faster, less secure)
config_fast = StationConfig(
    station_id="s1",
    station_name="Fast Station",
    enable_blockchain=False
)
```

**Trade-offs**:
- **Enable blockchain for**: Production, high-trust environments
- **Disable blockchain for**: Development, testing, time-critical applications

### Edge Optimization Trade-offs

```python
# With edge optimization (adaptive, slower)
config_adaptive = StationConfig(
    station_id="s1",
    station_name="Adaptive Station",
    enable_edge_optimization=True
)

# Without edge optimization (consistent, faster)
config_consistent = StationConfig(
    station_id="s1",
    station_name="Consistent Station",
    enable_edge_optimization=False
)
```

## Advanced Configuration

### Configuration Merging

```python
def merge_configs(base, overrides):
    """Merge configuration dictionaries."""
    result = base.copy()
    result.update(overrides)
    return result

base = {
    "station_id": "station",
    "station_name": "Station",
    "enable_blockchain": True
}

overrides = {
    "enable_blockchain": False,
    "cache_size_mb": 1000
}

merged = merge_configs(base, overrides)
# Result: {
#     'station_id': 'station',
#     'station_name': 'Station',
#     'enable_blockchain': False,
#     'cache_size_mb': 1000
# }
```

### Configuration Templating

```python
from string import Template

TEMPLATE = """
{
    "station_id": "$STATION_ID",
    "station_name": "$STATION_NAME",
    "cache_size_mb": $CACHE_SIZE,
    "enable_blockchain": $BLOCKCHAIN
}
"""

template = Template(TEMPLATE)
config_json = template.substitute(
    STATION_ID="s1",
    STATION_NAME="My Station",
    CACHE_SIZE="500",
    BLOCKCHAIN="true"
)
```

### Configuration Profiles

```python
class ConfigProfile:
    """Base class for configuration profiles."""

    def get_config(self):
        raise NotImplementedError

class MobileProfile(ConfigProfile):
    def get_config(self):
        return StationConfig(
            station_id="mobile",
            station_name="Mobile Station",
            max_playlist_size=20,
            streaming_quality="medium",
            cache_size_mb=200
        )

class DesktopProfile(ConfigProfile):
    def get_config(self):
        return StationConfig(
            station_id="desktop",
            station_name="Desktop Station",
            max_playlist_size=500,
            streaming_quality="lossless",
            cache_size_mb=2000
        )

# Use profiles
mobile_config = MobileProfile().get_config()
desktop_config = DesktopProfile().get_config()
```

## Configuration Examples

### Example 1: Minimal Configuration

```python
from qfzz.core.config import StationConfig

config = StationConfig(
    station_id="minimal_station",
    station_name="Minimal Station"
)
# Uses all defaults for other parameters
```

### Example 2: Complete Configuration

```python
from qfzz.core.config import StationConfig

config = StationConfig(
    # Identity
    station_id="complete_station",
    station_name="Complete QFZZ Station",

    # Playlist
    max_playlist_size=200,
    trust_threshold=0.7,

    # Features
    enable_blockchain=True,
    enable_edge_optimization=True,

    # Quality
    streaming_quality="high",
    cache_size_mb=1000,

    # Licensing
    allowed_licenses=[
        "CC-BY",
        "CC-BY-SA",
        "CC0",
        "CC-BY-NC"
    ],

    # Metadata
    metadata={
        "owner_id": "user_123",
        "region": "us-west",
        "tier": "premium",
        "created_at": "2024-01-01",
        "tags": ["rock", "indie", "alternative"]
    }
)
```

### Example 3: Multi-Device Configuration

```python
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

devices = {
    "phone": EdgeDeviceConfig(
        device_id="iphone_001",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=5.0,
        battery_powered=True
    ),
    "tablet": EdgeDeviceConfig(
        device_id="ipad_001",
        device_type=DeviceType.TABLET,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=10.0
    ),
    "desktop": EdgeDeviceConfig(
        device_id="mac_001",
        device_type=DeviceType.DESKTOP,
        network_type=NetworkType.ETHERNET,
        bandwidth_mbps=100.0
    )
}

# Each device gets optimized for its capabilities
for device_name, device_config in devices.items():
    print(f"{device_name}: {device_config.get_quality_tier()}")
    # Output:
    # phone: high
    # tablet: high
    # desktop: lossless
```

---

## Next Steps

1. **[Installation Guide](installation.md)** - Get QFZZ installed
2. **[Deployment Guide](deployment.md)** - Deploy to production
3. **[API Reference](../api-reference/)** - Explore the full API

## Support

For configuration issues:

1. **Check this guide** - Most common issues are covered
2. **Read documentation** - Full API documentation
3. **Ask community** - GitHub Discussions or Discord
