# Getting Started with QFZZ

This guide will walk you through installing QFZZ and creating your first personalized radio station.

## Installation

### Requirements

- Python 3.8 or higher
- pip or conda package manager
- (Optional) Firebase account for deployment

### Install from PyPI

The easiest way to install QFZZ:

```bash
pip install qfzz
```

### Install from Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/yourusername/qfzz.git
cd qfzz

# Install in development mode
pip install -e .

# Or with optional dependencies
pip install -e ".[dev,firebase]"
```

### Verify Installation

```python
import qfzz
print(qfzz.__version__)
```

## Your First Station

Let's create a basic QFZZ station with personalized recommendations.

### Step 1: Create a Station

```python
from qfzz import QFZZStation, StationConfig

# Create configuration
config = StationConfig(
    station_name="My First QFZZ Station",
    station_id="qfzz_001"
)

# Initialize station
station = QFZZStation(config)

# Start the station
station.start()
```

!!! success "Station Started!"
    Your QFZZ station is now running and ready to serve personalized content.

### Step 2: Add a Listener

```python
# Add yourself as a listener with preferences
station.add_listener(
    user_id="alice",
    preferences={
        'genres': {
            'rock': 0.8,
            'indie': 0.7,
            'electronic': 0.5
        },
        'energy_level': 0.7,  # 0.0 = calm, 1.0 = energetic
        'discovery_factor': 0.2  # 20% exploration
    }
)
```

### Step 3: Generate a Playlist

```python
# Generate personalized playlist
playlist = station.generate_playlist("alice")

# Display the playlist
for i, track in enumerate(playlist, 1):
    print(f"{i}. {track['title']} by {track['artist']} ({track['genre']})")
```

### Step 4: Record Feedback

```python
# User likes a track
station.record_interaction(
    user_id="alice",
    track_id=playlist[0]['track_id'],
    interaction_type="like",
    rating=0.9
)

# User skips a track
station.record_interaction(
    user_id="alice",
    track_id=playlist[1]['track_id'],
    interaction_type="skip"
)
```

### Step 5: Get Station Statistics

```python
# View station stats
stats = station.get_station_stats()
print(f"Station: {stats['station_name']}")
print(f"Listeners: {stats['listener_count']}")
print(f"Running: {stats['running']}")
```

## Complete Example

Here's a complete working example:

```python
from qfzz import QFZZStation, StationConfig

def main():
    # Configure station
    config = StationConfig(
        station_name="My Quantum Radio",
        station_id="qr_001",
        enable_blockchain=True,
        enable_edge_optimization=True,
        max_playlist_size=20,
        trust_threshold=0.5
    )

    # Create and start station
    station = QFZZStation(config)
    station.start()

    # Add multiple listeners
    listeners = [
        {
            'user_id': 'alice',
            'preferences': {
                'genres': {'rock': 0.8, 'indie': 0.6},
                'energy_level': 0.7
            }
        },
        {
            'user_id': 'bob',
            'preferences': {
                'genres': {'jazz': 0.9, 'blues': 0.7},
                'energy_level': 0.4
            }
        }
    ]

    for listener in listeners:
        station.add_listener(**listener)
        print(f"Added listener: {listener['user_id']}")

    # Generate playlists for each listener
    for listener in listeners:
        user_id = listener['user_id']
        playlist = station.generate_playlist(user_id)

        print(f"\n🎵 Playlist for {user_id}:")
        for i, track in enumerate(playlist[:5], 1):
            print(f"  {i}. {track['title']} - {track['artist']}")

    # Stop station when done
    station.stop()

if __name__ == "__main__":
    main()
```

## Enabling Advanced Features

### Blockchain Trust Network

Enable blockchain-based content verification:

```python
config = StationConfig(
    station_name="Secure Station",
    enable_blockchain=True,
    trust_threshold=0.6  # Only play content with trust >= 0.6
)

station = QFZZStation(config)
station.start()

# Access the trust network
trust_network = station._trust_network

# Add trust record
trust_network.add_trust_record(
    content_id="track_001",
    creator_id="artist_001",
    initial_score=0.8
)

# Verify content
trust_network.verify_content("track_001", "artist_001")

# Check trust score
score = trust_network.get_trust_score("track_001", "artist_001")
print(f"Trust score: {score}")
```

### Edge Optimization

Enable device-aware streaming optimization:

```python
from qfzz.edge import EdgeOptimizer, EdgeDeviceConfig, DeviceType, NetworkType

config = StationConfig(
    station_name="Optimized Station",
    enable_edge_optimization=True
)

station = QFZZStation(config)
station.start()

# Access the edge optimizer
optimizer = station._edge_optimizer

# Register a mobile device
device_config = EdgeDeviceConfig(
    device_id="mobile_001",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI,
    bandwidth_mbps=5.0,
    battery_powered=True,
    battery_level=0.3
)

optimizer.register_device(device_config)

# Get optimized streaming parameters
params = optimizer.optimize_streaming("mobile_001")
print(f"Quality: {params['quality']}")
print(f"Bitrate: {params['bitrate_kbps']} kbps")
print(f"Buffer: {params['buffer_size_seconds']} seconds")
```

### Dataset Management

Add and manage your music datasets:

```python
from qfzz.datasets import DatasetManager, Dataset, DatasetLicense

# Create dataset manager
manager = DatasetManager(
    allowed_licenses=['CC-BY', 'CC-BY-SA', 'CC0']
)

# Create a dataset
dataset = Dataset(
    dataset_id="indie_collection",
    name="Indie Rock Collection",
    description="Curated indie rock tracks",
    source="Local Library",
    license=DatasetLicense(
        license_type="CC-BY",
        commercial_use=True,
        derivative_works=True,
        share_alike=False
    )
)

# Add tracks to dataset
tracks = [
    {
        'track_id': 'indie_001',
        'title': 'Summer Nights',
        'artist': 'The Dreamers',
        'genre': 'indie',
        'duration': 234,
        'energy': 0.7
    },
    # ... more tracks
]

for track in tracks:
    dataset.add_track(track)

# Add to manager
if manager.add_dataset(dataset):
    print(f"Dataset added! Quality score: {dataset.quality_score}")

# List datasets
datasets = manager.list_datasets(min_quality=0.5)
for ds in datasets:
    print(f"{ds.name}: {ds.quality_score:.2f}")
```

## Configuration Options

### StationConfig

Complete configuration reference:

```python
config = StationConfig(
    # Basic settings
    station_name="My Station",           # Station display name
    station_id="station_001",            # Unique identifier

    # Feature toggles
    enable_blockchain=True,               # Enable trust network
    enable_edge_optimization=True,        # Enable device optimization

    # Playlist settings
    max_playlist_size=20,                 # Max tracks per playlist
    trust_threshold=0.5,                  # Min trust score (0.0-1.0)

    # Quality settings
    streaming_quality="high",             # low, medium, high, lossless

    # Licensing
    allowed_licenses=[                    # Allowed license types
        'CC-BY',
        'CC-BY-SA',
        'CC0'
    ]
)
```

## Next Steps

Now that you have a basic station running, explore:

1. **[Configuration Guide](guides/configuration.md)** - Detailed configuration options
2. **[Architecture Overview](architecture/overview.md)** - Understand how QFZZ works
3. **[PersonalizedDJ Deep Dive](features/personalized-dj.md)** - Master the AI DJ
4. **[Blockchain Trust](features/quantum-security.md)** - Secure your content
5. **[Edge Optimization](features/edge-optimization.md)** - Optimize for devices
6. **[Deployment Guide](guides/deployment.md)** - Deploy to production

## Troubleshooting

### Station won't start

```python
# Check if station is already running
if station.is_running():
    print("Station is already running!")
    station.stop()  # Stop first, then restart

station.start()
```

### Playlist is empty

```python
# Ensure listener is added
station.add_listener("user_id")

# Check if content catalog exists
# The DJ generates sample tracks by default
# but you can add your own content
from qfzz.dj import PersonalizedDJ

dj = station._dj
dj.add_content(my_tracks)  # Add your tracks
```

### Import errors

```bash
# Ensure QFZZ is properly installed
pip install --upgrade qfzz

# Or reinstall in development mode
pip install -e .
```

## Examples Repository

Find complete examples in the `examples/` directory:

- `basic_station.py` - Simple station setup
- `advanced_features.py` - All features enabled
- `multi_user.py` - Multiple listeners
- `dataset_management.py` - Working with datasets
- `blockchain_demo.py` - Trust network usage
- `edge_optimization.py` - Device optimization

## Getting Help

- **Documentation**: Browse the complete docs
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share ideas
- **Discord**: Chat with the community

---

**Next**: [Architecture Overview →](architecture/overview.md)
