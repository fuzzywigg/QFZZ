# Edge Optimization: Device-Aware Streaming and Caching

The `EdgeOptimizer` intelligently adapts streaming parameters to different device capabilities, network conditions, and user preferences. It ensures optimal playback quality and resource efficiency across all edge devices from smartphones to smart speakers.

## Overview

The EdgeOptimizer provides:

- **Device Profiles**: Support for 7 device types (smartphones, tablets, laptops, desktops, IoT, smart speakers, car systems)
- **Network Adaptation**: Dynamic optimization based on WiFi, 3G/4G/5G connections
- **Optimization Profiles**: 4 built-in profiles (power_save, balanced, quality, bandwidth_save)
- **Battery Awareness**: Smart power management for battery-powered devices
- **Caching Strategies**: Aggressive or conservative cache settings
- **Quality Tiers**: 4 quality levels (low, medium, high, lossless)

!!! info "Edge Computing"
    Edge optimization brings processing to the edge (user's device) rather than relying on centralized servers. This reduces latency, improves reliability, and respects user privacy.

## Architecture

### Core Components

The EdgeOptimizer consists of three main components:

```python
from qfzz.edge.optimizer import EdgeOptimizer
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

# Initialize optimizer
optimizer = EdgeOptimizer()

# Register a device
device = EdgeDeviceConfig(
    device_id='device_001',
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=10.0,
    cpu_cores=4,
    memory_mb=4096,
    storage_mb=32000,
    battery_powered=True,
    battery_level=0.9
)

optimizer.register_device(device)
```

**Key Classes**:

| Component | Purpose | Role |
|-----------|---------|------|
| `EdgeOptimizer` | Main orchestrator | Manages devices, optimization profiles |
| `EdgeDeviceConfig` | Device info | Stores device capabilities and state |
| `DeviceType` | Device classification | 7 device types |
| `NetworkType` | Network type | 6 network types |

## Device Management

### Device Types

The system supports 7 device types:

```python
from qfzz.edge.config import DeviceType

device_types = {
    DeviceType.SMARTPHONE: "Mobile phone",
    DeviceType.TABLET: "Tablet device",
    DeviceType.LAPTOP: "Portable computer",
    DeviceType.DESKTOP: "Stationary computer",
    DeviceType.IOT: "Internet of Things device",
    DeviceType.SMART_SPEAKER: "Voice-controlled speaker",
    DeviceType.CAR_SYSTEM: "In-vehicle system"
}
```

**Device Capabilities**:

| Device Type | CPU Cores | Memory | Storage | Battery | Hardware Decode | Max Bitrate |
|-----------|-----------|--------|---------|---------|-----------------|-------------|
| Smartphone | 4-8 | 2-8 GB | 32-512 GB | Yes | Yes | 256 kbps |
| Tablet | 4-8 | 2-8 GB | 32-512 GB | Yes | Yes | 256 kbps |
| Laptop | 2-8 | 4-32 GB | 256-1000 GB | Yes | Yes | 320 kbps |
| Desktop | 4-16 | 8-64 GB | 256-2000 GB | No | Yes | 320 kbps |
| IoT | 1-2 | 256-1024 MB | 4-32 GB | Maybe | No | 128 kbps |
| Smart Speaker | 1-2 | 512-2048 MB | 4-8 GB | No | No | 256 kbps |
| Car System | 2-4 | 1-4 GB | 16-64 GB | No | Yes | 256 kbps |

### Register Devices

Register a device with full capabilities:

```python
# Smartphone registration
smartphone = EdgeDeviceConfig(
    device_id='user_phone_01',
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=5.0,
    cpu_cores=6,
    memory_mb=4096,
    storage_mb=128000,
    battery_powered=True,
    battery_level=0.75,
    supports_hardware_decode=True,
    max_bitrate_kbps=256
)

optimizer.register_device(smartphone)

# Desktop registration
desktop = EdgeDeviceConfig(
    device_id='user_desktop_01',
    device_type=DeviceType.DESKTOP,
    network_type=NetworkType.ETHERNET,
    bandwidth_mbps=100.0,
    cpu_cores=8,
    memory_mb=16384,
    storage_mb=500000,
    battery_powered=False,
    battery_level=1.0,
    supports_hardware_decode=True,
    max_bitrate_kbps=320
)

optimizer.register_device(desktop)

# IoT device registration
iot = EdgeDeviceConfig(
    device_id='office_speaker',
    device_type=DeviceType.SMART_SPEAKER,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=2.0,
    cpu_cores=1,
    memory_mb=512,
    storage_mb=4000,
    battery_powered=False,
    supports_hardware_decode=False,
    max_bitrate_kbps=128
)

optimizer.register_device(iot)

print(f"Registered {len(optimizer._devices)} devices")
```

!!! tip "Device Registration"
    Register all user devices to enable seamless switching and device-aware optimization.

### Manage Device Lifecycle

```python
# Get device configuration
device = optimizer.get_device_config('user_phone_01')

if device:
    print(f"Device: {device.device_id}")
    print(f"Type: {device.device_type.value}")
    print(f"Bandwidth: {device.bandwidth_mbps} Mbps")
    print(f"Battery: {device.battery_level:.1%}")

# Unregister device
optimizer.unregister_device('old_device_id')
```

## Optimization Profiles

### Understanding Profiles

The EdgeOptimizer provides 4 optimization profiles:

```python
profiles = {
    'power_save': {
        'max_quality': 'medium',           # Lower quality saves battery
        'buffer_multiplier': 1.5,          # Larger buffer prevents stuttering
        'enable_hardware_decode': True,    # Hardware decode is efficient
        'aggressive_cache': True,          # Cache to reduce network usage
        'max_bitrate_kbps': 128            # Lower bitrate saves power
    },
    'balanced': {
        'max_quality': 'high',
        'buffer_multiplier': 1.0,
        'enable_hardware_decode': True,
        'aggressive_cache': False,
        'max_bitrate_kbps': 256
    },
    'quality': {
        'max_quality': 'lossless',         # Best audio quality
        'buffer_multiplier': 0.8,          # Smaller buffer is OK
        'enable_hardware_decode': True,
        'aggressive_cache': False,
        'max_bitrate_kbps': 320
    },
    'bandwidth_save': {
        'max_quality': 'low',              # Minimal bandwidth
        'buffer_multiplier': 2.0,          # Extra buffer handles delays
        'enable_hardware_decode': True,
        'aggressive_cache': True,          # Aggressive caching
        'max_bitrate_kbps': 96
    }
}
```

**Profile Selection Guide**:

| Profile | Use Case | Bandwidth | Battery | Quality |
|---------|----------|-----------|---------|---------|
| **power_save** | Low battery (< 30%) | No limit | Critical | Medium |
| **balanced** | Most situations | > 1 Mbps | Normal | High |
| **quality** | Fast WiFi, desktop | > 5 Mbps | N/A | Lossless |
| **bandwidth_save** | Cellular, 3G/4G | < 1 Mbps | Concern | Low |

### Profile Parameters

```python
def explain_profile(profile_name):
    """Explain what each profile parameter does."""
    
    explanations = {
        'max_quality': 'Maximum audio quality tier to use',
        'buffer_multiplier': 'Multiplier for default buffer size (1.0 = normal)',
        'enable_hardware_decode': 'Use hardware acceleration for decoding',
        'aggressive_cache': 'Cache entire tracks, not just next track',
        'max_bitrate_kbps': 'Maximum bitrate in kilobits per second'
    }
    
    profile = optimizer._optimization_profiles.get(profile_name)
    
    if profile:
        print(f"\n{profile_name.upper()} Profile:")
        for param, value in profile.items():
            print(f"  {param}: {value} - {explanations.get(param, '')}")

explain_profile('quality')
```

## Streaming Optimization

### Get Optimized Parameters

```python
# Get optimization for a device
optimization = optimizer.optimize_streaming(
    device_id='user_phone_01',
    preferences={'profile': 'balanced'}
)

print("Streaming Optimization:")
print(f"  Device: {optimization['device_id']}")
print(f"  Profile: {optimization['profile']}")
print(f"  Quality: {optimization['quality']}")
print(f"  Bitrate: {optimization['bitrate_kbps']} kbps")
print(f"  Buffer: {optimization['buffer_size_seconds']} seconds")
print(f"  Hardware Decode: {optimization['use_hardware_decode']}")
print(f"  Cache Enabled: {optimization['cache_enabled']}")
print(f"  Cache Size: {optimization['cache_size_mb']} MB")
print(f"  Preload Tracks: {optimization['preload_tracks']}")
```

**Optimization Output**:

```python
{
    'device_id': 'user_phone_01',
    'profile': 'balanced',
    'quality': 'high',                 # Quality tier
    'bitrate_kbps': 256,               # Recommended bitrate
    'buffer_size_seconds': 15,         # Pre-buffer before playback
    'use_hardware_decode': True,       # Use hardware acceleration
    'cache_enabled': True,             # Enable caching
    'cache_size_mb': 100,              # Cache size allocation
    'preload_tracks': 3                # How many next tracks to cache
}
```

### Quality Tiers

The system supports 4 quality tiers:

```python
quality_tiers = {
    'low': {
        'bitrate_kbps': 96,
        'sample_rate': 22050,
        'format': 'MP3 or AAC',
        'use_case': 'Cellular 3G, limited bandwidth'
    },
    'medium': {
        'bitrate_kbps': 128,
        'sample_rate': 44100,
        'format': 'AAC or Ogg Vorbis',
        'use_case': 'Cellular 4G, average bandwidth'
    },
    'high': {
        'bitrate_kbps': 256,
        'sample_rate': 44100,
        'format': 'AAC or Ogg Vorbis',
        'use_case': 'WiFi, good bandwidth'
    },
    'lossless': {
        'bitrate_kbps': 320,
        'sample_rate': 48000,
        'format': 'FLAC or ALAC',
        'use_case': 'Ethernet, excellent bandwidth'
    }
}
```

**Quality Recommendations by Device**:

```python
def recommend_quality_for_device(device):
    """Recommend quality tier based on device capabilities."""
    
    quality_order = ['low', 'medium', 'high', 'lossless']
    
    # Consider bandwidth
    if device.bandwidth_mbps >= 5.0:
        quality_idx = 3  # lossless
    elif device.bandwidth_mbps >= 2.0:
        quality_idx = 2  # high
    elif device.bandwidth_mbps >= 1.0:
        quality_idx = 1  # medium
    else:
        quality_idx = 0  # low
    
    # Consider device type
    if device.device_type in [DeviceType.SMARTPHONE, DeviceType.TABLET]:
        quality_idx = min(quality_idx, 2)  # Cap at high
    elif device.device_type in [DeviceType.SMART_SPEAKER, DeviceType.IOT]:
        quality_idx = min(quality_idx, 1)  # Cap at medium
    
    return quality_order[quality_idx]

quality = recommend_quality_for_device(smartphone)
print(f"Recommended quality: {quality}")
```

### Custom Optimization

```python
# Get optimization with custom preferences
optimization = optimizer.optimize_streaming(
    device_id='user_phone_01',
    preferences={
        'profile': 'balanced',
        'quality': 'high'  # User preference
    }
)

print(f"Quality: {optimization['quality']}")
print(f"Bitrate: {optimization['bitrate_kbps']} kbps")
```

## Network Adaptation

### Update Network Conditions

Dynamically update network information:

```python
# User switches to WiFi
optimizer.update_network_conditions(
    device_id='user_phone_01',
    network_type=NetworkType.WIFI,
    bandwidth_mbps=25.0
)

# Network degrades
optimizer.update_network_conditions(
    device_id='user_phone_01',
    network_type=NetworkType.CELLULAR_4G,
    bandwidth_mbps=2.0
)

# Very poor connection
optimizer.update_network_conditions(
    device_id='user_phone_01',
    network_type=NetworkType.CELLULAR_3G,
    bandwidth_mbps=0.5
)

# Get updated optimization
opt = optimizer.optimize_streaming('user_phone_01')
print(f"New profile: {opt['profile']}")
print(f"New bitrate: {opt['bitrate_kbps']} kbps")
```

**Network Types**:

| Network | Bandwidth | Quality | Use Case |
|---------|-----------|---------|----------|
| Ethernet | > 100 Mbps | Excellent | Desktop, high-quality |
| WiFi | 5-50 Mbps | Good | Home, office |
| 5G Cellular | 20-100 Mbps | Excellent | Mobile, future |
| 4G Cellular | 5-20 Mbps | Good | Mobile |
| 3G Cellular | 0.5-5 Mbps | Fair | Mobile, fallback |
| Unknown | Auto-detect | Unknown | Fallback |

### Adaptive Bitrate

```python
def adaptive_bitrate_streaming(optimizer, device_id):
    """Example of adaptive bitrate streaming."""
    
    device = optimizer.get_device_config(device_id)
    
    if not device:
        return None
    
    # Calculate bitrate based on available bandwidth
    # Use 80% of available bandwidth
    available_bitrate = device.bandwidth_mbps * 1024 * 0.8  # Convert to kbps
    
    # Apply profile limits
    profile_name = optimizer._select_profile(device, None)
    profile = optimizer._optimization_profiles[profile_name]
    max_profile_bitrate = profile['max_bitrate_kbps']
    
    # Use minimum of available and profile max
    recommended_bitrate = min(int(available_bitrate), max_profile_bitrate)
    
    return {
        'device_id': device_id,
        'available_bandwidth_mbps': device.bandwidth_mbps,
        'recommended_bitrate_kbps': recommended_bitrate,
        'profile': profile_name
    }

# Get adaptive bitrate
adaptive = adaptive_bitrate_streaming(optimizer, 'user_phone_01')
print(f"Adaptive bitrate: {adaptive['recommended_bitrate_kbps']} kbps")
```

## Battery Management

### Monitor Battery Status

```python
# Update battery level
optimizer.update_battery_status(
    device_id='user_phone_01',
    battery_level=0.50  # 50% battery
)

# Check current optimization
opt = optimizer.optimize_streaming('user_phone_01')
print(f"Current profile: {opt['profile']}")

# Simulate low battery
optimizer.update_battery_status('user_phone_01', battery_level=0.15)
opt_low = optimizer.optimize_streaming('user_phone_01')
print(f"Profile at 15% battery: {opt_low['profile']}")
```

### Battery Thresholds

```python
battery_thresholds = {
    'normal': {
        'threshold': 0.3,
        'profile': 'balanced',
        'description': 'Normal usage'
    },
    'low': {
        'threshold': 0.15,
        'profile': 'power_save',
        'description': 'Switch to power-saving mode'
    },
    'critical': {
        'threshold': 0.05,
        'profile': 'power_save',
        'max_quality': 'low',
        'description': 'Emergency power saving'
    }
}
```

## Caching Strategies

### Cache Settings

```python
# Get cache configuration
opt = optimizer.optimize_streaming('user_phone_01')

cache_config = {
    'enabled': opt['cache_enabled'],
    'size_mb': opt['cache_size_mb'],
    'preload_count': opt['preload_tracks']
}

print(f"Cache Configuration:")
print(f"  Enabled: {cache_config['enabled']}")
print(f"  Size: {cache_config['size_mb']} MB")
print(f"  Preload: {cache_config['preload_count']} tracks")
```

### Cache Strategy Selection

```python
def select_cache_strategy(device):
    """Select caching strategy based on device."""
    
    strategies = {
        'aggressive': {
            'enabled': True,
            'cache_full_track': True,
            'preload_count': 5,
            'use_case': 'Cellular, unstable network'
        },
        'moderate': {
            'enabled': True,
            'cache_next_track': True,
            'preload_count': 3,
            'use_case': 'Mixed network conditions'
        },
        'minimal': {
            'enabled': False,
            'preload_count': 0,
            'use_case': 'Fast, stable connection'
        }
    }
    
    # Select based on network and device
    if device.network_type in [NetworkType.CELLULAR_3G, NetworkType.CELLULAR_4G]:
        return strategies['aggressive']
    elif device.bandwidth_mbps < 2.0:
        return strategies['aggressive']
    elif device.battery_powered and device.battery_level < 0.3:
        return strategies['aggressive']
    elif device.network_type == NetworkType.WIFI:
        return strategies['moderate']
    else:
        return strategies['minimal']

# Select strategy
strategy = select_cache_strategy(smartphone)
print(f"Cache Strategy: {strategy['use_case']}")
```

## Advanced Patterns

### Device Capability Detection

```python
def detect_device_capabilities(device_id):
    """Automatically detect device capabilities."""
    
    # In a real system, this would probe the device
    # For now, return based on device type
    
    capabilities = {
        'hardware_video_decode': True,
        'hardware_audio_decode': True,
        'background_playback': True,
        'audio_offloading': True,
        'spatial_audio': False,
        'dolby_atmos': False,
        'hires_audio': False
    }
    
    device = optimizer.get_device_config(device_id)
    
    if device:
        # Smartphones typically don't support spatial audio
        if device.device_type == DeviceType.SMARTPHONE:
            capabilities['spatial_audio'] = False
        
        # Desktop systems might support it
        if device.device_type == DeviceType.DESKTOP:
            capabilities['spatial_audio'] = True
            capabilities['hires_audio'] = True
        
        # IoT devices have limited capabilities
        if device.device_type in [DeviceType.SMART_SPEAKER, DeviceType.IOT]:
            capabilities['hardware_video_decode'] = False
            capabilities['background_playback'] = False
    
    return capabilities

# Check capabilities
caps = detect_device_capabilities('user_phone_01')
print(f"Spatial Audio: {caps['spatial_audio']}")
print(f"Hires Audio: {caps['hires_audio']}")
```

### Multi-Device Synchronization

```python
def sync_optimization_across_devices(optimizer, user_devices):
    """Synchronize optimization settings across user's devices."""
    
    # Get user preferences (e.g., from profile)
    user_preferences = {
        'preferred_quality': 'high',
        'battery_mode': False,
        'cache_aggressive': False
    }
    
    optimizations = {}
    
    for device_id in user_devices:
        # Get device
        device = optimizer.get_device_config(device_id)
        if not device:
            continue
        
        # Adjust preferences based on device
        device_prefs = user_preferences.copy()
        
        # Override for low-battery devices
        if device.battery_powered and device.battery_level < 0.3:
            device_prefs['battery_mode'] = True
            device_prefs['preferred_quality'] = 'medium'
        
        # Get optimization
        opt = optimizer.optimize_streaming(device_id, device_prefs)
        optimizations[device_id] = opt
    
    return optimizations

# Sync across devices
user_devices = ['user_phone_01', 'user_tablet_01', 'user_desktop_01']
synced = sync_optimization_across_devices(optimizer, user_devices)

for device_id, opt in synced.items():
    print(f"{device_id}: {opt['profile']} - {opt['quality']}")
```

### Dynamic Profile Selection

```python
def intelligent_profile_selection(optimizer, device_id):
    """Intelligently select profile based on multiple factors."""
    
    device = optimizer.get_device_config(device_id)
    if not device:
        return 'balanced'
    
    scores = {
        'power_save': 0,
        'bandwidth_save': 0,
        'balanced': 0,
        'quality': 0
    }
    
    # Battery status
    if device.battery_powered:
        if device.battery_level < 0.2:
            scores['power_save'] += 10
        elif device.battery_level < 0.4:
            scores['power_save'] += 5
    
    # Network conditions
    if device.bandwidth_mbps < 0.5:
        scores['bandwidth_save'] += 10
    elif device.bandwidth_mbps < 1.0:
        scores['bandwidth_save'] += 5
    elif device.bandwidth_mbps > 5.0:
        scores['quality'] += 5
    
    # Network type
    if device.network_type == NetworkType.CELLULAR_3G:
        scores['bandwidth_save'] += 10
    elif device.network_type == NetworkType.WIFI:
        scores['balanced'] += 5
    elif device.network_type == NetworkType.ETHERNET:
        scores['quality'] += 10
    
    # Device type
    if device.device_type in [DeviceType.DESKTOP, DeviceType.LAPTOP]:
        scores['quality'] += 3
    elif device.device_type in [DeviceType.IOT, DeviceType.SMART_SPEAKER]:
        scores['bandwidth_save'] += 3
    
    # Default to balanced
    scores['balanced'] += 2
    
    # Return profile with highest score
    return max(scores, key=scores.get)

# Get intelligent profile
profile = intelligent_profile_selection(optimizer, 'user_phone_01')
print(f"Intelligent profile: {profile}")
```

## Statistics and Monitoring

### Get Optimizer Statistics

```python
stats = optimizer.get_statistics()

print("Optimizer Statistics:")
print(f"  Total Devices: {stats['total_devices']}")
print(f"  Device Types: {stats['device_types']}")
print(f"  Profiles: {', '.join(stats['available_profiles'])}")

# Device distribution
for device_type, count in stats['device_types'].items():
    print(f"    {device_type}: {count} devices")
```

### Device Health Monitoring

```python
def monitor_device_health(optimizer, device_id):
    """Monitor device health and performance."""
    
    device = optimizer.get_device_config(device_id)
    if not device:
        return None
    
    health = {
        'device_id': device_id,
        'status': 'HEALTHY',
        'issues': []
    }
    
    # Check battery
    if device.battery_powered:
        if device.battery_level < 0.1:
            health['issues'].append('Critical battery level')
            health['status'] = 'WARNING'
        elif device.battery_level < 0.2:
            health['issues'].append('Low battery')
    
    # Check bandwidth
    if device.bandwidth_mbps < 0.5:
        health['issues'].append('Very low bandwidth')
        health['status'] = 'WARNING'
    
    # Check storage
    if device.storage_mb < 1000:
        health['issues'].append('Limited storage')
    
    # Check memory
    if device.memory_mb < 512:
        health['issues'].append('Limited memory')
        health['status'] = 'WARNING'
    
    return health

# Monitor device
health = monitor_device_health(optimizer, 'user_phone_01')
if health:
    print(f"Device Health: {health['status']}")
    for issue in health['issues']:
        print(f"  ⚠️  {issue}")
```

## Integration with Other Features

### With Dataset Management

```python
from qfzz.datasets import DatasetManager

manager = DatasetManager()
optimizer = EdgeOptimizer()

def get_dataset_for_device(manager, optimizer, device_id):
    """Select appropriate dataset for device."""
    
    device = optimizer.get_device_config(device_id)
    if not device:
        return None
    
    # Get all datasets
    datasets = manager.list_datasets()
    
    # Filter by device capability
    suitable = []
    for dataset in datasets:
        # Skip if quality too low
        if dataset.quality_score < 0.6:
            continue
        
        # Skip if too large for device
        total_duration = dataset.get_total_duration()
        
        # Estimate storage needed (256 kbps average)
        estimated_mb = (total_duration / 3600) * (256 / 8) / 1024
        
        if estimated_mb > device.storage_mb * 0.5:  # Use max 50% of storage
            continue
        
        suitable.append(dataset)
    
    # Return highest quality dataset
    if suitable:
        return sorted(suitable, key=lambda d: d.quality_score, reverse=True)[0]
    
    return None
```

### With PersonalizedDJ

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ()
optimizer = EdgeOptimizer()

def get_optimized_playlist(dj, optimizer, user_id, device_id):
    """Generate playlist optimized for device."""
    
    # Get device optimization
    opt = optimizer.optimize_streaming(device_id)
    
    # Generate playlist
    playlist = dj.generate_playlist(user_id)
    
    # Adjust playlist for device
    # - Limit number of tracks based on storage
    # - Suggest quality based on bandwidth
    # - Recommend cache settings
    
    return {
        'playlist': playlist,
        'optimization': opt,
        'notes': f"Optimized for {opt['quality']} quality at {opt['bitrate_kbps']} kbps"
    }
```

## Best Practices

### 1. Register All User Devices

```python
# Register all devices for comprehensive optimization
devices = [
    ('phone', DeviceType.SMARTPHONE),
    ('tablet', DeviceType.TABLET),
    ('desktop', DeviceType.DESKTOP)
]

for device_id, device_type in devices:
    config = EdgeDeviceConfig(
        device_id=device_id,
        device_type=device_type,
        # ... other parameters
    )
    optimizer.register_device(config)
```

### 2. Monitor Network Changes

```python
# Detect network changes and update
def network_change_handler(device_id, new_bandwidth, new_network_type):
    """Handle network change event."""
    
    optimizer.update_network_conditions(
        device_id=device_id,
        network_type=new_network_type,
        bandwidth_mbps=new_bandwidth
    )
    
    # Get updated optimization
    opt = optimizer.optimize_streaming(device_id)
    print(f"Optimization updated: {opt['profile']}")
```

### 3. Respond to Battery Changes

```python
# Update optimization when battery changes
def battery_change_handler(device_id, new_battery_level):
    """Handle battery change event."""
    
    optimizer.update_battery_status(device_id, new_battery_level)
    
    if new_battery_level < 0.3:
        print(f"⚠️ Low battery on {device_id}")
        # Update optimization
        opt = optimizer.optimize_streaming(device_id)
        print(f"Switched to: {opt['profile']}")
```

### 4. Cache Intelligently

```python
# Implement smart caching based on optimization
def setup_caching(device_id):
    """Setup device caching based on optimization."""
    
    opt = optimizer.optimize_streaming(device_id)
    
    cache_config = {
        'enabled': opt['cache_enabled'],
        'size_mb': opt['cache_size_mb'],
        'preload_tracks': opt['preload_tracks'],
        'preload_on_wifi': True,
        'clear_on_low_storage': True
    }
    
    return cache_config
```

## Performance Optimization

### Efficient Device Lookups

```python
# The optimizer uses a device index for O(1) lookups
device = optimizer.get_device_config('device_001')  # O(1)

# Get optimization with caching
def get_cached_optimization(optimizer, device_id):
    """Get optimization with result caching."""
    
    # First call computes
    opt1 = optimizer.optimize_streaming(device_id)
    
    # Subsequent calls reuse computation
    opt2 = optimizer.optimize_streaming(device_id)
    
    return opt2
```

### Batch Device Updates

```python
def batch_update_devices(optimizer, updates):
    """Efficiently update multiple devices."""
    
    for device_id, network_info in updates.items():
        optimizer.update_network_conditions(
            device_id=device_id,
            network_type=network_info['type'],
            bandwidth_mbps=network_info['bandwidth']
        )
```

## Testing Edge Optimization

```python
def test_edge_optimization():
    """Test edge optimization functionality."""
    
    optimizer = EdgeOptimizer()
    
    # Register test device
    device = EdgeDeviceConfig(
        device_id='test_device',
        device_type=DeviceType.SMARTPHONE,
        bandwidth_mbps=5.0,
        battery_powered=True,
        battery_level=0.8
    )
    
    optimizer.register_device(device)
    
    # Test optimization
    opt = optimizer.optimize_streaming('test_device')
    assert opt['device_id'] == 'test_device'
    assert opt['quality'] in ['low', 'medium', 'high', 'lossless']
    
    # Test network update
    optimizer.update_network_conditions(
        'test_device',
        NetworkType.CELLULAR_3G,
        0.5
    )
    
    opt2 = optimizer.optimize_streaming('test_device')
    assert opt2['profile'] in ['power_save', 'balanced', 'quality', 'bandwidth_save']
    
    # Test battery update
    optimizer.update_battery_status('test_device', 0.1)
    opt3 = optimizer.optimize_streaming('test_device')
    assert opt3['profile'] == 'power_save'
    
    print("✓ All edge optimization tests passed")

test_edge_optimization()
```

## Troubleshooting

### Issue: Poor Performance on Device

```python
def diagnose_device_performance(optimizer, device_id):
    """Diagnose performance issues on a device."""
    
    device = optimizer.get_device_config(device_id)
    if not device:
        return None
    
    issues = []
    
    # Check bandwidth
    if device.bandwidth_mbps < 1.0:
        issues.append(f"Low bandwidth: {device.bandwidth_mbps} Mbps")
    
    # Check battery
    if device.battery_powered and device.battery_level < 0.2:
        issues.append(f"Low battery: {device.battery_level:.1%}")
    
    # Check memory
    if device.memory_mb < 512:
        issues.append(f"Low memory: {device.memory_mb} MB")
    
    # Check storage
    if device.storage_mb < 1000:
        issues.append(f"Low storage: {device.storage_mb} MB")
    
    return issues

issues = diagnose_device_performance(optimizer, 'problem_device')
if issues:
    for issue in issues:
        print(f"⚠️ {issue}")
```

## Roadmap

See [Roadmap](../roadmap.md) for planned enhancements:

- [ ] AI-powered profile selection
- [ ] Predictive bandwidth estimation
- [ ] Device fingerprinting
- [ ] Cross-device playback synchronization
- [ ] Network-aware buffering strategies
- [ ] Hardware capability auto-detection
- [ ] Geographic optimization (CDN routing)
- [ ] Environmental adaptation (noise, temperature)

---

**Next**: [Dataset Management →](dataset-management.md) | [Blockchain Trust →](quantum-security.md) | [API Reference →](../api-reference/edge.md)
