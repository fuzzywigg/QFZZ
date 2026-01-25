# EdgeOptimizer, EdgeDeviceConfig, DeviceType, and NetworkType API Reference

## Overview

The edge module optimizes streaming parameters for diverse devices ranging from smartphones to smart speakers, adapting quality, buffering, caching, and bitrate based on device capabilities and network conditions. The `EdgeOptimizer` class dynamically adjusts streaming settings, while `EdgeDeviceConfig` provides device capability specification with `DeviceType` and `NetworkType` enums for precise configuration.

## Table of Contents

- [EdgeOptimizer Class](#edgeoptimizer-class)
  - [Constructor](#constructor)
  - [Device Management](#device-management)
  - [Optimization](#optimization)
  - [Network and Battery Updates](#network-and-battery-updates)
  - [Statistics](#statistics)
- [EdgeDeviceConfig Class](#edgedeviceconfig-class)
  - [Constructor](#constructor-1)
  - [Quality and Buffer Calculation](#quality-and-buffer-calculation)
  - [Cache Recommendations](#cache-recommendations)
  - [Validation](#validation)
- [DeviceType Enum](#devicetype-enum)
- [NetworkType Enum](#networktype-enum)
- [Code Examples](#code-examples)
- [Optimization Profiles](#optimization-profiles)

---

## EdgeOptimizer Class

### Constructor

```python
def __init__(self) -> None
```

Initialize the Edge Optimizer.

**Parameters:** None

**Returns:** None

**Side Effects:**
- Initializes empty devices registry
- Sets up optimization profiles
- Logs initialization

**Optimization Profiles:**

Four built-in profiles are created:

| Profile | Quality | Buffer | Hardware | Cache | Bitrate |
|---------|---------|--------|----------|-------|---------|
| power_save | medium | 1.5× | Yes | Aggressive | 128 kbps |
| balanced | high | 1.0× | Yes | No | 256 kbps |
| quality | lossless | 0.8× | Yes | No | 320 kbps |
| bandwidth_save | low | 2.0× | Yes | Aggressive | 96 kbps |

**Example:**

```python
from qfzz.edge.optimizer import EdgeOptimizer

optimizer = EdgeOptimizer()
print("EdgeOptimizer initialized with 4 profiles")
```

---

## Device Management

### register_device()

```python
def register_device(self, config: EdgeDeviceConfig) -> None
```

Register a device for optimization.

**Parameters:**

- `config` (EdgeDeviceConfig): Device configuration

**Returns:** None

**Raises:**
- `ValueError`: If config validation fails

**Side Effects:**
- Stores device config in registry
- Logs device registration

**Example:**

```python
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

# Register smartphone
phone_config = EdgeDeviceConfig(
    device_id="user_001_phone",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=5.0,
    cpu_cores=4,
    memory_mb=4096,
    storage_mb=32768,
    battery_powered=True,
    battery_level=0.75,
    supports_hardware_decode=True,
    max_bitrate_kbps=256
)

optimizer.register_device(phone_config)

# Register laptop
laptop_config = EdgeDeviceConfig(
    device_id="user_001_laptop",
    device_type=DeviceType.LAPTOP,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=50.0,
    cpu_cores=8,
    memory_mb=16384,
    storage_mb=512000,
    battery_powered=True,
    battery_level=0.9,
    supports_hardware_decode=True,
    max_bitrate_kbps=320
)

optimizer.register_device(laptop_config)

# Register smart speaker
speaker_config = EdgeDeviceConfig(
    device_id="user_001_speaker",
    device_type=DeviceType.SMART_SPEAKER,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=10.0,
    cpu_cores=2,
    memory_mb=512,
    storage_mb=2048,
    battery_powered=False,
    supports_hardware_decode=True,
    max_bitrate_kbps=192
)

optimizer.register_device(speaker_config)
```

---

### unregister_device()

```python
def unregister_device(self, device_id: str) -> bool
```

Unregister a device.

**Parameters:**

- `device_id` (str): Device identifier

**Returns:** bool - True if unregistered, False if not found

**Side Effects:**
- Removes device from registry
- Logs unregistration

**Example:**

```python
if optimizer.unregister_device("user_001_phone"):
    print("Phone unregistered")
else:
    print("Device not found")
```

---

### get_device_config()

```python
def get_device_config(self, device_id: str) -> Optional[EdgeDeviceConfig]
```

Retrieve device configuration.

**Parameters:**

- `device_id` (str): Device identifier

**Returns:** EdgeDeviceConfig if found, None otherwise

**Example:**

```python
config = optimizer.get_device_config("user_001_phone")
if config:
    print(f"Device: {config.device_type.value}")
    print(f"Network: {config.network_type.value}")
    print(f"Bandwidth: {config.bandwidth_mbps} Mbps")
else:
    print("Device not found")
```

---

## Optimization

### optimize_streaming()

```python
def optimize_streaming(self, device_id: str, 
                      preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
```

Generate optimized streaming parameters for a device.

**Parameters:**

- `device_id` (str): Device identifier
- `preferences` (Optional[Dict[str, Any]]): Optional user preferences:
  - `profile` (str): Force specific profile (power_save, balanced, quality, bandwidth_save)
  - `quality` (str): Force quality tier (low, medium, high, lossless)

**Returns:** Dict containing optimized parameters:
- `device_id` (str): Device identifier
- `profile` (str): Selected optimization profile
- `quality` (str): Quality tier (low, medium, high, lossless)
- `bitrate_kbps` (int): Streaming bitrate in kbps
- `buffer_size_seconds` (int): Buffer duration in seconds
- `use_hardware_decode` (bool): Enable hardware decoding
- `cache_enabled` (bool): Cache enabled
- `cache_size_mb` (int): Cache size in MB
- `preload_tracks` (int): Tracks to preload

**Raises:**
- `ValueError`: If device_id not found

**Optimization Logic:**

1. **Profile Selection**: Based on device state and preferences
2. **Quality Calculation**: Based on device capabilities and profile
3. **Bitrate Calculation**: Based on quality and bandwidth
4. **Buffer Calculation**: Based on network stability
5. **Cache Settings**: Based on device storage and network

**Example:**

```python
# Basic optimization
settings = optimizer.optimize_streaming("user_001_phone")
print(f"Profile: {settings['profile']}")
print(f"Quality: {settings['quality']}")
print(f"Bitrate: {settings['bitrate_kbps']} kbps")
print(f"Buffer: {settings['buffer_size_seconds']}s")
print(f"Cache: {settings['cache_size_mb']}MB")

# With preferences
settings = optimizer.optimize_streaming(
    "user_001_phone",
    preferences={
        "quality": "high",
        "profile": "balanced"
    }
)
```

---

### update_network_conditions()

```python
def update_network_conditions(self, device_id: str, 
                             network_type: NetworkType,
                             bandwidth_mbps: float) -> None
```

Update network conditions for a device.

**Parameters:**

- `device_id` (str): Device identifier
- `network_type` (NetworkType): Current network type
- `bandwidth_mbps` (float): Current bandwidth in Mbps

**Returns:** None

**Raises:**
- `ValueError`: If device_id not found

**Side Effects:**
- Updates device's network_type
- Updates device's bandwidth_mbps
- Logs update

**Example:**

```python
# User switches from WiFi to cellular
optimizer.update_network_conditions(
    "user_001_phone",
    NetworkType.CELLULAR_4G,
    bandwidth_mbps=2.5
)

# Get updated optimization
new_settings = optimizer.optimize_streaming("user_001_phone")
print(f"New bitrate: {new_settings['bitrate_kbps']} kbps")

# User returns to WiFi
optimizer.update_network_conditions(
    "user_001_phone",
    NetworkType.WIFI,
    bandwidth_mbps=20.0
)
```

---

### update_battery_status()

```python
def update_battery_status(self, device_id: str, battery_level: float) -> None
```

Update battery status for a device.

**Parameters:**

- `device_id` (str): Device identifier
- `battery_level` (float): Battery level (0.0-1.0)

**Returns:** None

**Raises:**
- `ValueError`: If device_id not found
- `ValueError`: If battery_level out of range

**Side Effects:**
- Updates device's battery_level
- Logs update
- Warns if not a battery device

**Example:**

```python
# Simulate battery drain
for level in [0.8, 0.5, 0.2]:
    optimizer.update_battery_status("user_001_phone", level)
    settings = optimizer.optimize_streaming("user_001_phone")
    print(f"Battery {level:.0%}: Profile={settings['profile']}")

# Output:
# Battery 80%: Profile=balanced
# Battery 50%: Profile=balanced
# Battery 20%: Profile=power_save
```

---

## Statistics

### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

Get optimizer statistics.

**Parameters:** None

**Returns:** Dict containing:
- `total_devices` (int): Number of registered devices
- `device_types` (Dict[str, int]): Count by device type
- `available_profiles` (List[str]): Available profiles

**Example:**

```python
stats = optimizer.get_statistics()
print(f"=== Optimizer Statistics ===")
print(f"Total devices: {stats['total_devices']}")
print(f"Device types: {stats['device_types']}")
print(f"Profiles: {', '.join(stats['available_profiles'])}")

# Output example:
# Total devices: 3
# Device types: {'smartphone': 1, 'laptop': 1, 'smart_speaker': 1}
# Profiles: ['power_save', 'balanced', 'quality', 'bandwidth_save']
```

---

## EdgeDeviceConfig Class

### Constructor

```python
@dataclass
class EdgeDeviceConfig:
    device_id: str
    device_type: DeviceType
    network_type: NetworkType = NetworkType.UNKNOWN
    bandwidth_mbps: float = 10.0
    cpu_cores: int = 2
    memory_mb: int = 2048
    storage_mb: int = 1024
    battery_powered: bool = False
    battery_level: float = 1.0
    supports_hardware_decode: bool = True
    max_bitrate_kbps: int = 320
    metadata: Dict[str, Any] = field(default_factory=dict)
```

Create device configuration.

**Parameters:**

- `device_id` (str): Unique device identifier
- `device_type` (DeviceType): Device type enum
- `network_type` (NetworkType): Network connection, default UNKNOWN
- `bandwidth_mbps` (float): Available bandwidth, default 10.0
- `cpu_cores` (int): CPU cores, default 2
- `memory_mb` (int): RAM in MB, default 2048
- `storage_mb` (int): Storage in MB, default 1024
- `battery_powered` (bool): Is battery device, default False
- `battery_level` (float): Battery level 0-1, default 1.0
- `supports_hardware_decode` (bool): Hardware decoding support, default True
- `max_bitrate_kbps` (int): Max bitrate, default 320
- `metadata` (Dict): Custom metadata, default empty

**Raises:** ValueError if validation fails

**Example:**

```python
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

# High-end smartphone
phone = EdgeDeviceConfig(
    device_id="iphone_14",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=30.0,
    cpu_cores=6,
    memory_mb=6144,
    storage_mb=128000,
    battery_powered=True,
    battery_level=0.85,
    max_bitrate_kbps=320,
    metadata={
        "model": "iPhone 14 Pro",
        "os": "iOS 16"
    }
)

# Budget Android phone
budget_phone = EdgeDeviceConfig(
    device_id="android_budget",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=3.0,
    cpu_cores=2,
    memory_mb=2048,
    storage_mb=32000,
    battery_powered=True,
    battery_level=0.5,
    max_bitrate_kbps=192
)

# IoT device
iot = EdgeDeviceConfig(
    device_id="iot_device",
    device_type=DeviceType.IOT,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=5.0,
    cpu_cores=1,
    memory_mb=256,
    storage_mb=512,
    battery_powered=True,
    battery_level=0.9,
    supports_hardware_decode=False,
    max_bitrate_kbps=96
)
```

---

## Quality and Buffer Calculation

### get_quality_tier()

```python
def get_quality_tier(self) -> str
```

Get recommended quality tier based on device capabilities.

**Parameters:** None

**Returns:** str - Quality tier: 'low', 'medium', 'high', or 'lossless'

**Selection Logic:**

```
If bandwidth >= 5.0 AND (desktop OR laptop):
    return 'lossless'  # 320 kbps, uncompressed
elif bandwidth >= 2.0:
    return 'high'      # 256 kbps
elif bandwidth >= 1.0:
    return 'medium'    # 128 kbps
else:
    return 'low'       # 96 kbps
```

**Example:**

```python
phone = EdgeDeviceConfig(
    device_id="phone1",
    device_type=DeviceType.SMARTPHONE,
    bandwidth_mbps=2.5
)

tier = phone.get_quality_tier()
print(f"Quality: {tier}")  # "high"

# Low bandwidth device
device = EdgeDeviceConfig(
    device_id="iot1",
    device_type=DeviceType.IOT,
    bandwidth_mbps=0.5
)

tier = device.get_quality_tier()
print(f"Quality: {tier}")  # "low"
```

---

### get_buffer_size_seconds()

```python
def get_buffer_size_seconds(self) -> int
```

Get recommended buffer size in seconds.

**Parameters:** None

**Returns:** int - Buffer size in seconds

**Selection Logic:**

```
If network == CELLULAR_3G:
    return 30  # Very unstable, need large buffer
elif network in (CELLULAR_4G, CELLULAR_5G):
    return 15  # Moderately stable
else:
    return 10  # WiFi/ethernet, stable
```

**Example:**

```python
# 3G device
device_3g = EdgeDeviceConfig(
    device_id="old_phone",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_3G
)

buffer = device_3g.get_buffer_size_seconds()
print(f"Buffer: {buffer}s")  # 30

# WiFi device
device_wifi = EdgeDeviceConfig(
    device_id="laptop",
    device_type=DeviceType.LAPTOP,
    network_type=NetworkType.WIFI
)

buffer = device_wifi.get_buffer_size_seconds()
print(f"Buffer: {buffer}s")  # 10
```

---

## Cache Recommendations

### should_use_cache()

```python
def should_use_cache(self) -> bool
```

Determine if device should use aggressive caching.

**Parameters:** None

**Returns:** bool - True if caching recommended

**Decision Logic:**

```
If network in (CELLULAR_3G, CELLULAR_4G):
    return True  # Cellular is expensive
elif bandwidth < 2.0:
    return True  # Limited bandwidth
elif battery_powered AND battery_level < 0.3:
    return True  # Low battery
else:
    return False
```

**Example:**

```python
# Cellular device - should cache
phone = EdgeDeviceConfig(
    device_id="phone1",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_4G
)

print(phone.should_use_cache())  # True

# High-bandwidth WiFi - no caching needed
desktop = EdgeDeviceConfig(
    device_id="desktop1",
    device_type=DeviceType.DESKTOP,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=100.0
)

print(desktop.should_use_cache())  # False
```

---

## Validation

### validate()

```python
def validate(self) -> None
```

Validate configuration parameters.

**Parameters:** None

**Returns:** None

**Raises:** ValueError if any parameter invalid

**Validation Rules:**

- `device_id`: Must be non-empty
- `bandwidth_mbps`: Must be >= 0
- `cpu_cores`: Must be > 0
- `memory_mb`: Must be >= 0
- `storage_mb`: Must be >= 0
- `battery_level`: Must be 0.0-1.0
- `max_bitrate_kbps`: Must be >= 0

**Example:**

```python
try:
    config = EdgeDeviceConfig(
        device_id="test",
        device_type=DeviceType.SMARTPHONE,
        bandwidth_mbps=-1  # Invalid!
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

---

### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

Convert configuration to dictionary.

**Parameters:** None

**Returns:** Dict with all config attributes

**Example:**

```python
config_dict = config.to_dict()
print(config_dict)
# {
#     'device_id': 'phone1',
#     'device_type': 'smartphone',
#     'network_type': '4g',
#     'bandwidth_mbps': 5.0,
#     ...
# }
```

---

## DeviceType Enum

Supported edge device types:

```python
class DeviceType(Enum):
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    IOT = "iot"
    SMART_SPEAKER = "smart_speaker"
    CAR_SYSTEM = "car_system"
```

**Usage:**

```python
from qfzz.edge.config import DeviceType

# Create device of each type
phone = EdgeDeviceConfig(
    device_id="phone1",
    device_type=DeviceType.SMARTPHONE
)

speaker = EdgeDeviceConfig(
    device_id="speaker1",
    device_type=DeviceType.SMART_SPEAKER
)

car = EdgeDeviceConfig(
    device_id="car1",
    device_type=DeviceType.CAR_SYSTEM
)
```

---

## NetworkType Enum

Supported network connection types:

```python
class NetworkType(Enum):
    WIFI = "wifi"
    CELLULAR_5G = "5g"
    CELLULAR_4G = "4g"
    CELLULAR_3G = "3g"
    ETHERNET = "ethernet"
    UNKNOWN = "unknown"
```

**Typical Bandwidth:**

| Type | Typical Bandwidth |
|------|-------------------|
| CELLULAR_3G | 0.5-2 Mbps |
| CELLULAR_4G | 5-20 Mbps |
| CELLULAR_5G | 50-500 Mbps |
| WIFI | 10-100+ Mbps |
| ETHERNET | 100+ Mbps |

**Usage:**

```python
from qfzz.edge.config import NetworkType

# Create device with specific network
phone = EdgeDeviceConfig(
    device_id="phone1",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=10.0
)
```

---

## Code Examples

### Complete Edge Optimization Workflow

```python
from qfzz.edge.optimizer import EdgeOptimizer
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

# Initialize optimizer
optimizer = EdgeOptimizer()

# Register diverse devices
devices = [
    EdgeDeviceConfig(
        device_id="user_001_phone",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.CELLULAR_4G,
        bandwidth_mbps=5.0,
        battery_powered=True,
        battery_level=0.8
    ),
    EdgeDeviceConfig(
        device_id="user_001_laptop",
        device_type=DeviceType.LAPTOP,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=50.0,
        battery_powered=True,
        battery_level=0.9,
        max_bitrate_kbps=320
    ),
    EdgeDeviceConfig(
        device_id="user_001_speaker",
        device_type=DeviceType.SMART_SPEAKER,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=10.0,
        battery_powered=False,
        max_bitrate_kbps=192
    )
]

for config in devices:
    optimizer.register_device(config)

print("=== Initial Optimization ===")
for device_id in ["user_001_phone", "user_001_laptop", "user_001_speaker"]:
    settings = optimizer.optimize_streaming(device_id)
    print(f"{device_id}:")
    print(f"  Profile: {settings['profile']}")
    print(f"  Quality: {settings['quality']}")
    print(f"  Bitrate: {settings['bitrate_kbps']} kbps")
    print(f"  Buffer: {settings['buffer_size_seconds']}s")
    print(f"  Cache: {settings['cache_size_mb']}MB")

# Update phone to poor network
print("\n=== Phone Switches to Poor Signal ===")
optimizer.update_network_conditions(
    "user_001_phone",
    NetworkType.CELLULAR_3G,
    bandwidth_mbps=0.8
)

settings = optimizer.optimize_streaming("user_001_phone")
print(f"New bitrate: {settings['bitrate_kbps']} kbps")
print(f"New buffer: {settings['buffer_size_seconds']}s")

# Simulate low battery
print("\n=== Phone Battery Low ===")
optimizer.update_battery_status("user_001_phone", 0.15)

settings = optimizer.optimize_streaming("user_001_phone")
print(f"Profile: {settings['profile']}")  # power_save
print(f"Quality: {settings['quality']}")  # Reduced

# Get statistics
print("\n=== Statistics ===")
stats = optimizer.get_statistics()
print(f"Total devices: {stats['total_devices']}")
print(f"Device types: {stats['device_types']}")
```

### Adaptive Streaming Simulation

```python
def simulate_network_change():
    """Simulate device streaming with changing network."""
    optimizer = EdgeOptimizer()
    
    device = EdgeDeviceConfig(
        device_id="test_device",
        device_type=DeviceType.SMARTPHONE,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=20.0,
        battery_powered=True,
        battery_level=0.9
    )
    
    optimizer.register_device(device)
    
    # Scenario: User on WiFi
    print("=== WiFi (Good) ===")
    settings = optimizer.optimize_streaming("test_device")
    print(f"Quality: {settings['quality']}")
    print(f"Bitrate: {settings['bitrate_kbps']} kbps")
    
    # User leaves WiFi, connects to 4G
    print("\n=== 4G (Medium) ===")
    optimizer.update_network_conditions(
        "test_device",
        NetworkType.CELLULAR_4G,
        bandwidth_mbps=10.0
    )
    settings = optimizer.optimize_streaming("test_device")
    print(f"Quality: {settings['quality']}")
    print(f"Bitrate: {settings['bitrate_kbps']} kbps")
    
    # User enters 3G coverage area
    print("\n=== 3G (Poor) ===")
    optimizer.update_network_conditions(
        "test_device",
        NetworkType.CELLULAR_3G,
        bandwidth_mbps=1.5
    )
    settings = optimizer.optimize_streaming("test_device")
    print(f"Quality: {settings['quality']}")
    print(f"Bitrate: {settings['bitrate_kbps']} kbps")
    print(f"Buffer: {settings['buffer_size_seconds']}s")  # Increased
    
    # Battery also drains
    print("\n=== 3G + Low Battery ===")
    optimizer.update_battery_status("test_device", 0.2)
    settings = optimizer.optimize_streaming("test_device")
    print(f"Profile: {settings['profile']}")  # power_save
    print(f"Cache: {settings['cache_size_mb']}MB")  # Aggressive

simulate_network_change()
```

---

## Optimization Profiles

### Profile Comparison

| Aspect | Power Save | Balanced | Quality | Bandwidth Save |
|--------|-----------|----------|---------|----------------|
| **Quality** | Medium | High | Lossless | Low |
| **Max Bitrate** | 128 | 256 | 320 | 96 |
| **Buffer** | 1.5× | 1.0× | 0.8× | 2.0× |
| **Cache** | Aggressive | No | No | Aggressive |
| **Hardware Decode** | Yes | Yes | Yes | Yes |
| **Use Case** | Low battery | Normal | Desktop/WiFi | Limited data |

### Profile Selection Logic

The optimizer automatically selects profiles based on device state:

```
1. Check user preference
   If provided, use if within constraints
   
2. Auto-select based on state
   If low battery (< 30%) AND mobile:
       → power_save
   
   If cellular (3G/4G):
       → bandwidth_save
   
   If bandwidth < 1 Mbps:
       → bandwidth_save
   
   If high bandwidth (>= 5) AND (desktop/laptop):
       → quality
   
   Otherwise:
       → balanced
```

---

## Version Information

- **Module**: `qfzz.edge.optimizer`, `qfzz.edge.config`
- **Classes**: `EdgeOptimizer`, `EdgeDeviceConfig`
- **Enums**: `DeviceType`, `NetworkType`
- **Python**: 3.8+
- **Dependencies**: dataclasses, typing, enum

