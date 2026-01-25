# Edge Device Deployment Guide

This guide covers deploying QFZZ on edge devices, enabling users to run their personal AI DJ locally on smartphones, smart speakers, and embedded systems.

## Table of Contents

1. [Overview](#overview)
2. [Supported Edge Device Types](#supported-edge-device-types)
3. [Model Optimization Strategies](#model-optimization-strategies)
4. [Memory Management](#memory-management)
5. [Network Optimization for 6G](#network-optimization-for-6g)
6. [Caching Strategies](#caching-strategies)
7. [Configuration Examples](#configuration-examples)
8. [Performance Tips](#performance-tips)
9. [Troubleshooting](#troubleshooting)

## Overview

QFZZ is designed for edge-first deployment, meaning the AI DJ runs directly on your device rather than in the cloud. This approach provides:

- **Privacy**: Your data stays on your device
- **Low Latency**: No round-trip to cloud servers
- **Offline Capability**: Works without constant connectivity
- **Personalization**: Models adapt to your specific usage patterns

The edge deployment system consists of two main components:

1. **EdgeOptimizer** - Optimizes models and streaming for device constraints
2. **EdgeDeviceConfig** - Device-specific configuration and limits

See the [Edge API Documentation](../api/edge.md) for detailed API reference.

## Supported Edge Device Types

### 1. Smartphones

Modern smartphones (iOS/Android) with typical specifications:

**Hardware Profile**:
- Memory: 2-8 GB RAM
- Storage: 8-16 GB available
- CPU: ARM64 (Apple Silicon, Snapdragon, MediaTek)
- Network: 4G/5G/WiFi

**Recommended Configuration**:
```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer

config = EdgeDeviceConfig(
    device_id="user_smartphone_001",
    device_type="smartphone",
    max_memory_mb=2048,          # 2 GB RAM for QFZZ
    max_model_size_mb=150,       # Up to 150 MB model
    enable_6g=True,              # If 6G available
    network_bandwidth_mbps=200,  # Typical 5G/6G bandwidth
    storage_available_gb=8.0     # 8 GB for cache
)

optimizer = EdgeOptimizer(config)
```

**Optimal Use Cases**:
- High-quality audio streaming (320 kbps)
- Real-time DJ interactions
- Large model support
- Extensive local caching

### 2. Smart Speakers

Dedicated audio devices (Amazon Echo, Google Home, Apple HomePod):

**Hardware Profile**:
- Memory: 512 MB - 2 GB RAM
- Storage: 1-4 GB available
- CPU: ARM Cortex-A (various)
- Network: WiFi only

**Recommended Configuration**:
```python
config = EdgeDeviceConfig(
    device_id="home_speaker_001",
    device_type="smart_speaker",
    max_memory_mb=512,           # Limited RAM
    max_model_size_mb=80,        # Smaller model required
    enable_6g=False,             # WiFi only
    network_bandwidth_mbps=100,  # WiFi 5/6
    storage_available_gb=2.0     # Limited storage
)

optimizer = EdgeOptimizer(config)
```

**Optimal Use Cases**:
- Voice-first interaction
- Background music streaming
- Smaller models with quantization
- Modest caching

### 3. Embedded Devices

Raspberry Pi, custom hardware, IoT devices:

**Hardware Profile**:
- Memory: 256 MB - 1 GB RAM
- Storage: 512 MB - 2 GB available
- CPU: ARM Cortex-A7/A53
- Network: WiFi/Ethernet

**Recommended Configuration**:
```python
config = EdgeDeviceConfig(
    device_id="embedded_rpi_001",
    device_type="embedded",
    max_memory_mb=256,           # Very limited RAM
    max_model_size_mb=50,        # Tiny model only
    enable_6g=False,             # WiFi/Ethernet
    network_bandwidth_mbps=50,   # Limited bandwidth
    storage_available_gb=1.0     # Minimal storage
)

optimizer = EdgeOptimizer(config)
```

**Optimal Use Cases**:
- Headless operation
- Minimal model (heavily quantized)
- Stream-only mode (minimal caching)
- Local network deployment

## Model Optimization Strategies

The EdgeOptimizer automatically recommends optimizations based on device constraints. Here's how to optimize your models:

### Quantization

Convert model weights from FP32 (32-bit floating point) to INT8 (8-bit integer) for 4x size reduction:

**Example**:
```python
from qfzz.edge import EdgeOptimizer, EdgeDeviceConfig

# Configure for embedded device
config = EdgeDeviceConfig(
    device_id="edge_001",
    device_type="embedded",
    max_model_size_mb=50  # Only 50 MB available
)

optimizer = EdgeOptimizer(config)

# Check if model needs optimization
original_size = 200.0  # 200 MB original model
recommendations = optimizer.optimize_model(original_size)

print(recommendations)
# Output:
# {
#     'original_size_mb': 200.0,
#     'target_size_mb': 50.0,
#     'optimizations': ['quantization', 'pruning']
# }
```

**Quantization Benefits**:
- **Size**: 4x reduction (200 MB → 50 MB)
- **Speed**: 2-4x faster inference
- **Memory**: 4x less RAM usage
- **Accuracy**: Minimal loss (<2% typically)

**Quantization Trade-offs**:
- Slight quality degradation in responses
- Better for conversational AI than precision tasks
- Test thoroughly before deployment

### Pruning

Remove unnecessary weights and neurons to reduce model size:

**When to Prune**:
- Model still too large after quantization
- Need additional 20-50% size reduction
- Can tolerate slight quality loss

**Pruning Strategy**:
1. Start with quantization (always apply first)
2. Apply structured pruning (remove entire neurons)
3. Retrain briefly to recover accuracy
4. Test conversational quality

**Example Implementation** (conceptual):
```python
# After quantization, if model still too large
if recommendations['optimizations']:
    if 'pruning' in recommendations['optimizations']:
        # Apply pruning to reach target size
        prune_ratio = 0.3  # Remove 30% of weights
        # In production, use libraries like:
        # - torch.nn.utils.prune (PyTorch)
        # - tensorflow_model_optimization (TensorFlow)
```

### Model Distillation

Train a smaller "student" model to mimic a larger "teacher" model:

**Distillation Use Cases**:
- Going from cloud (10 GB) to edge (<100 MB)
- Creating device-specific models
- Maintaining quality with 10-50x size reduction

**Benefits**:
- Better quality than direct compression
- Optimized for specific tasks
- Can target specific device profiles

### Choosing the Right Strategy

| Device Type | Model Size | Recommended Strategies |
|-------------|------------|------------------------|
| Smartphone | 100-150 MB | Quantization (INT8) |
| Smart Speaker | 50-80 MB | Quantization + Light Pruning |
| Embedded | 20-50 MB | Quantization + Heavy Pruning + Distillation |

## Memory Management

Efficient memory usage is critical for edge deployment. The EdgeOptimizer includes memory management features:

### Memory Constraints

Different devices have different memory profiles:

```python
# Check device memory status
status = optimizer.get_device_status()
print(f"Memory limit: {status['memory_limit_mb']} MB")
print(f"Cache size: {status['cache_size_mb']} MB")
```

### Memory Budget Allocation

Typical memory allocation for a 512 MB device:

- **Model weights**: 100 MB (20%)
- **Runtime memory**: 256 MB (50%)
- **Audio buffers**: 64 MB (12.5%)
- **Cache**: 92 MB (17.5%)

### Memory Optimization Techniques

#### 1. Lazy Loading

Load model components only when needed:

```python
# Don't load entire model at startup
# Load conversation model on first interaction
# Load music analysis model when recommending

# In production, implement lazy loading:
class LazyModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
    
    def predict(self, input_data):
        if self.model is None:
            self.model = load_model(self.model_path)
        return self.model.predict(input_data)
```

#### 2. Streaming Inference

Process data in chunks rather than loading entirely:

```python
# Instead of loading full audio into memory:
# for chunk in audio_stream:
#     process_chunk(chunk)
#     # Release memory after processing

# Streaming keeps memory constant regardless of input size
```

#### 3. Cache Eviction

Remove old cache entries when memory is tight:

```python
# EdgeOptimizer implements LRU caching
# Oldest items removed when storage is 80% full

# Check before caching
if optimizer.can_cache_locally(size_mb=10.0):
    optimizer.add_to_cache("track_123", audio_data, 10.0)
else:
    print("Cache full, streaming only")
```

#### 4. Memory Pooling

Reuse allocated memory buffers:

```python
# Instead of: buffer = new_buffer(size)  # Every time
# Use: buffer = buffer_pool.get(size)    # Reuse

# Reduces garbage collection overhead
# Especially important on embedded devices
```

## Network Optimization for 6G

QFZZ is designed to leverage 6G networks when available, with fallbacks for 4G/5G/WiFi.

### 6G Benefits

- **Ultra-low latency**: <1ms round-trip time
- **High bandwidth**: 1+ Gbps per device
- **Reliability**: 99.999% uptime
- **Edge computing**: Distributed processing at cell tower

### Enabling 6G Mode

```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer

# Enable 6G features
config = EdgeDeviceConfig(
    device_id="6g_smartphone_001",
    device_type="smartphone",
    max_memory_mb=2048,
    max_model_size_mb=150,
    enable_6g=True,              # Enable 6G optimizations
    network_bandwidth_mbps=1000, # 1 Gbps available
    storage_available_gb=8.0
)

optimizer = EdgeOptimizer(config)
```

### Optimized Streaming with 6G

The optimizer automatically adjusts streaming parameters:

```python
# Request high-quality audio
streaming_config = optimizer.optimize_streaming(bitrate_kbps=320)

print(streaming_config)
# With 6G enabled:
# {
#     'recommended_bitrate_kbps': 320,  # Full quality
#     'buffer_ms': 100,                  # Minimal buffer
#     'enable_compression': True,
#     'adaptive_quality': False          # No need to adapt
# }
```

### 6G vs Non-6G Comparison

| Feature | 6G Mode | Non-6G Mode |
|---------|---------|-------------|
| Bitrate | 320 kbps (fixed) | Adaptive (128-320 kbps) |
| Buffer | 100 ms | 1000 ms |
| Quality | Consistent high | Variable |
| Latency | <1 ms | 10-100 ms |
| Adaptive | No (unnecessary) | Yes (required) |

### Fallback Strategy

When 6G is unavailable, the optimizer automatically adapts:

```python
# Same code works with or without 6G
streaming_config = optimizer.optimize_streaming(bitrate_kbps=320)

# Without 6G, optimizer returns:
# {
#     'recommended_bitrate_kbps': 224,   # Adapted to bandwidth
#     'buffer_ms': 1000,                 # Larger buffer
#     'enable_compression': True,
#     'adaptive_quality': True           # Dynamic adjustment
# }
```

### Network Bandwidth Detection

The optimizer respects configured bandwidth limits:

```python
# With 100 Mbps connection
config = EdgeDeviceConfig(
    device_id="device_001",
    device_type="smartphone",
    network_bandwidth_mbps=100,  # 100 Mbps available
    enable_6g=False
)

optimizer = EdgeOptimizer(config)

# Optimizer uses 70% of bandwidth for safety
# max_bitrate = 100 * 1000 * 0.7 = 70,000 kbps
# Recommended: min(requested, max_bitrate)
```

## Caching Strategies

Local caching reduces bandwidth usage and improves response time.

### Cache Management

The EdgeOptimizer includes built-in cache management:

```python
from qfzz.edge import EdgeOptimizer, EdgeDeviceConfig

config = EdgeDeviceConfig(
    device_id="device_001",
    device_type="smartphone",
    storage_available_gb=8.0  # 8 GB available for cache
)

optimizer = EdgeOptimizer(config)

# Add content to cache
track_data = load_track("track_123.mp3")
track_size_mb = 5.0

if optimizer.can_cache_locally(track_size_mb):
    optimizer.add_to_cache("track_123", track_data, track_size_mb)
    print("Track cached locally")
else:
    print("Insufficient storage, will stream")

# Retrieve from cache
cached_track = optimizer.get_from_cache("track_123")
if cached_track:
    print("Playing from cache (instant)")
else:
    print("Streaming from network")
```

### Cache Size Limits

The optimizer uses 80% of available storage for caching:

```python
# With 8 GB available storage:
# Max cache size = 8 * 1024 * 0.8 = 6,553.6 MB

# This leaves 20% for system and other apps
```

### What to Cache

**Priority 1 - Frequently Played**:
- User's favorite tracks
- Recently played music
- DJ response templates

**Priority 2 - Likely Needed**:
- Recommended tracks
- Popular community tracks
- Genre-specific collections

**Priority 3 - Nice to Have**:
- Full albums
- Playlist tracks
- Discovery queue

### Cache Eviction Policy

When cache is full, oldest items are removed (LRU - Least Recently Used):

```python
# Automatic LRU eviction when adding new content
# 1. Check: will new content fit?
# 2. If not: remove oldest until space available
# 3. Add new content

# Manual cache clearing when needed
optimizer.clear_cache()
print("Cache cleared")
```

### Monitoring Cache Usage

```python
# Get device status including cache info
status = optimizer.get_device_status()

print(f"Cache size: {status['cache_size_mb']:.1f} MB")
print(f"Cache items: {status['cache_items']}")
print(f"Storage available: {config.storage_available_gb} GB")

# Calculate cache utilization
max_cache_mb = config.storage_available_gb * 1024 * 0.8
utilization = (status['cache_size_mb'] / max_cache_mb) * 100
print(f"Cache utilization: {utilization:.1f}%")
```

## Configuration Examples

### Complete Edge Deployment Setup

Here's a complete example integrating edge optimization with the PersonalizedDJ:

```python
from qfzz import QFZZStation
from qfzz.core import StationConfig
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer
from qfzz.dj import PersonalizedDJ

# 1. Configure edge device
edge_config = EdgeDeviceConfig(
    device_id="my_smartphone_001",
    device_type="smartphone",
    max_memory_mb=2048,
    max_model_size_mb=150,
    enable_6g=True,
    network_bandwidth_mbps=500,
    storage_available_gb=10.0
)

# 2. Initialize edge optimizer
optimizer = EdgeOptimizer(edge_config)

# 3. Check model optimization needs
model_size_mb = 200.0  # Original model size
optimization = optimizer.optimize_model(model_size_mb)

if optimization['optimizations']:
    print(f"Apply optimizations: {optimization['optimizations']}")
    print(f"Target size: {optimization['target_size_mb']} MB")
else:
    print("No optimization needed")

# 4. Configure streaming
streaming_config = optimizer.optimize_streaming(bitrate_kbps=320)
print(f"Streaming at {streaming_config['recommended_bitrate_kbps']} kbps")
print(f"Buffer: {streaming_config['buffer_ms']} ms")

# 5. Initialize QFZZ station
station_config = StationConfig(
    station_name="My Personal QFZZ",
    edge_mode=True,
    enable_6g=edge_config.enable_6g,
    blockchain_enabled=True,
    enable_personalization=True
)

station = QFZZStation(config=station_config)
station.start()

# 6. Get your personalized DJ
dj = station.get_dj()

# 7. Start interacting
greeting = dj.greet_user("user_001", "Alex")
print(greeting)

response = dj.interact("user_001", "Play something energetic!")
print(response)

# 8. Cache management
track_id = "energetic_track_001"
track_size_mb = 4.5

if optimizer.can_cache_locally(track_size_mb):
    # Cache track for offline playback
    track_data = load_track_from_network(track_id)
    optimizer.add_to_cache(track_id, track_data, track_size_mb)
    print(f"Cached {track_id} for offline access")

# 9. Monitor device status
status = optimizer.get_device_status()
print(f"Device: {status['device_type']}")
print(f"6G: {'enabled' if status['6g_enabled'] else 'disabled'}")
print(f"Cache: {status['cache_size_mb']:.1f} MB ({status['cache_items']} items)")
```

### Minimal Configuration (Embedded Device)

For very constrained devices:

```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer

# Minimal config for Raspberry Pi Zero
config = EdgeDeviceConfig(
    device_id="rpi_zero_001",
    device_type="embedded",
    max_memory_mb=256,       # Very limited
    max_model_size_mb=30,    # Tiny model
    enable_6g=False,
    network_bandwidth_mbps=25,  # WiFi only
    storage_available_gb=0.5    # 512 MB cache
)

optimizer = EdgeOptimizer(config)

# Use lowest quality streaming
streaming_config = optimizer.optimize_streaming(bitrate_kbps=128)
print(f"Bitrate: {streaming_config['recommended_bitrate_kbps']} kbps")

# Minimal caching - only essential data
if optimizer.can_cache_locally(1.0):  # 1 MB
    optimizer.add_to_cache("dj_responses", response_templates, 1.0)
```

### Cloud-Edge Hybrid Configuration

For devices that can offload to cloud when needed:

```python
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer

# Smartphone with cloud fallback
config = EdgeDeviceConfig(
    device_id="hybrid_phone_001",
    device_type="smartphone",
    max_memory_mb=1024,
    max_model_size_mb=100,     # Medium model
    enable_6g=True,
    network_bandwidth_mbps=500,
    storage_available_gb=5.0
)

optimizer = EdgeOptimizer(config)

# Determine what to run locally vs cloud
if optimizer.can_cache_locally(model_size_mb=100):
    mode = "full_local"  # Run everything on device
else:
    mode = "hybrid"      # Complex tasks to cloud

print(f"Running in {mode} mode")
```

## Performance Tips

### 1. Pre-warm Cache

Cache essential content during setup:

```python
# At app startup or during WiFi connection
essential_tracks = ["welcome_track", "default_playlist"]

for track_id in essential_tracks:
    if optimizer.can_cache_locally(5.0):
        track_data = download_track(track_id)
        optimizer.add_to_cache(track_id, track_data, 5.0)
```

### 2. Monitor and Adjust

Continuously monitor performance:

```python
import time

# Check device status periodically
def monitor_device():
    status = optimizer.get_device_status()
    
    # Alert if cache too large
    cache_limit = config.storage_available_gb * 1024 * 0.8
    if status['cache_size_mb'] > cache_limit * 0.9:
        print("Warning: Cache nearly full")
        # Consider clearing old items
    
    # Alert if many cache misses
    # (implement miss tracking)

# Run every 5 minutes
while True:
    monitor_device()
    time.sleep(300)
```

### 3. Batch Operations

Batch cache operations for efficiency:

```python
# Instead of adding tracks one by one
# Batch check and add multiple tracks

tracks_to_cache = [
    ("track_1", data_1, 5.0),
    ("track_2", data_2, 4.5),
    ("track_3", data_3, 6.0)
]

total_size = sum(size for _, _, size in tracks_to_cache)

if optimizer.can_cache_locally(total_size):
    for track_id, data, size in tracks_to_cache:
        optimizer.add_to_cache(track_id, data, size)
    print(f"Batch cached {len(tracks_to_cache)} tracks")
```

### 4. Optimize Model Loading

Load models efficiently:

```python
# Use memory-mapped files for large models
# Load only required model components
# Implement model sharing across users (if device supports multiple users)

# Example: Lazy loading
class OptimizedDJ:
    def __init__(self):
        self.conversation_model = None
        self.music_model = None
    
    def chat(self, message):
        if self.conversation_model is None:
            self.conversation_model = load_conversation_model()
        return self.conversation_model.respond(message)
    
    def recommend(self, preferences):
        if self.music_model is None:
            self.music_model = load_music_model()
        return self.music_model.recommend(preferences)
```

### 5. Network Optimization

Optimize network usage:

```python
# Use compression for all network requests
optimizer.compression_enabled = True

# Implement request coalescing
# Batch multiple small requests into one

# Use streaming config effectively
streaming_config = optimizer.optimize_streaming(bitrate_kbps=320)

# Adjust based on actual network conditions
if network_quality_poor():
    # Request lower bitrate
    streaming_config = optimizer.optimize_streaming(bitrate_kbps=128)
```

## Troubleshooting

### Problem: Model Too Large

**Symptoms**: Model won't load, out of memory errors

**Solution**:
```python
# Check model size recommendations
model_size = 200.0  # MB
recommendations = optimizer.optimize_model(model_size)

if recommendations['optimizations']:
    print("Model too large!")
    print(f"Target size: {recommendations['target_size_mb']} MB")
    print(f"Apply: {recommendations['optimizations']}")
    
    # Actions:
    # 1. Apply quantization (FP32 → INT8)
    # 2. Apply pruning if still too large
    # 3. Use smaller base model
    # 4. Consider cloud offload for this device
```

### Problem: Cache Always Full

**Symptoms**: Constant cache evictions, can't cache new content

**Solution**:
```python
# Check cache status
status = optimizer.get_device_status()
cache_limit_mb = config.storage_available_gb * 1024 * 0.8

print(f"Cache: {status['cache_size_mb']:.1f} / {cache_limit_mb:.1f} MB")

if status['cache_size_mb'] > cache_limit_mb * 0.9:
    # Actions:
    # 1. Clear old cache manually
    optimizer.clear_cache()
    
    # 2. Reduce storage allocation
    config.storage_available_gb = 2.0  # Reduce from 8 GB to 2 GB
    
    # 3. Cache only essentials
    # Only cache user favorites, not discovery queue
```

### Problem: Poor Streaming Quality

**Symptoms**: Buffering, stuttering, dropouts

**Solution**:
```python
# Check streaming configuration
streaming_config = optimizer.optimize_streaming(bitrate_kbps=320)

print(f"Recommended bitrate: {streaming_config['recommended_bitrate_kbps']} kbps")
print(f"Buffer: {streaming_config['buffer_ms']} ms")

if streaming_config['adaptive_quality']:
    # Network can't sustain high quality
    # Actions:
    # 1. Lower requested bitrate
    streaming_config = optimizer.optimize_streaming(bitrate_kbps=128)
    
    # 2. Increase buffer size (custom implementation)
    buffer_ms = 2000  # 2 seconds instead of 1 second
    
    # 3. Enable aggressive caching
    # Pre-cache next tracks in queue
```

### Problem: High Memory Usage

**Symptoms**: Device slow, apps killed, crashes

**Solution**:
```python
# Check memory configuration
print(f"Memory limit: {config.max_memory_mb} MB")

# Actions:
# 1. Reduce memory allocation
config.max_memory_mb = 256  # Reduce limit

# 2. Implement streaming inference (don't load full data)

# 3. Clear caches more aggressively
optimizer.clear_cache()

# 4. Use smaller model
config.max_model_size_mb = 50  # Reduce model size
recommendations = optimizer.optimize_model(100.0)
```

### Problem: 6G Not Working

**Symptoms**: Falls back to slower network despite 6G availability

**Solution**:
```python
# Verify 6G configuration
print(f"6G enabled: {config.enable_6g}")
print(f"Bandwidth: {config.network_bandwidth_mbps} Mbps")

# Actions:
# 1. Ensure 6G is enabled in config
config.enable_6g = True

# 2. Verify network bandwidth is high enough
if config.network_bandwidth_mbps < 500:
    print("Bandwidth too low for optimal 6G features")
    config.network_bandwidth_mbps = 1000  # 1 Gbps

# 3. Check device actually has 6G capability
# (implementation-specific check)

# 4. Test with streaming config
streaming_config = optimizer.optimize_streaming(bitrate_kbps=320)
if streaming_config['buffer_ms'] > 200:
    print("6G features not fully enabled")
```

### Problem: Slow Model Inference

**Symptoms**: DJ responses slow, poor user experience

**Solution**:
```python
# Profile model performance
import time

start = time.time()
response = dj.interact("user_001", "Hello")
duration = time.time() - start

print(f"Response time: {duration:.2f}s")

if duration > 2.0:  # More than 2 seconds
    # Actions:
    # 1. Apply quantization for faster inference
    recommendations = optimizer.optimize_model(model_size_mb)
    if 'quantization' not in recommendations['optimizations']:
        print("Consider quantization for speed")
    
    # 2. Reduce model size
    config.max_model_size_mb = 50  # Smaller = faster
    
    # 3. Use GPU acceleration (if available)
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 4. Implement response caching
    # Cache common responses to avoid re-computation
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# EdgeOptimizer will log detailed information
logger = logging.getLogger('qfzz.edge')
logger.setLevel(logging.DEBUG)

# Now see detailed logs:
# DEBUG: Edge optimizer initialized for smartphone (6G: True)
# DEBUG: Cached track_123 (5.0MB)
# DEBUG: Cache size: 15.5 MB (3 items)
```

## Next Steps

- **[PersonalizedDJ Guide](personalized-dj.md)** - Learn about the DJ system
- **[API Reference](../api/edge.md)** - Detailed edge API documentation
- **[Architecture](../architecture.md)** - Understand system design
- **Examples** - See `examples/edge_optimization.py` in the repository

## Support

For issues and questions:
- Check [troubleshooting](#troubleshooting) section above
- Review the examples directory in the repository
- Open an issue on GitHub
- Consult [API documentation](../api/edge.md)
