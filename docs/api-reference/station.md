# QFZZStation API Reference

## Overview

The `QFZZStation` class is the main orchestrator for a QFZZ Radio Station. It coordinates personalized DJ recommendations, dataset management, blockchain trust verification, edge optimization, and streaming capabilities. The station manages multiple listeners and provides a unified interface for all station operations.

## Table of Contents

- [QFZZStation Class](#qfzzstation-class)
  - [Constructor](#constructor)
  - [Core Methods](#core-methods)
  - [Listener Management](#listener-management)
  - [Playlist Generation](#playlist-generation)
  - [Interaction Recording](#interaction-recording)
  - [Statistics](#statistics)
- [Code Examples](#code-examples)
- [Error Handling](#error-handling)

---

## QFZZStation Class

### Constructor

```python
QFZZStation(config: StationConfig) -> None
```

Initialize a QFZZ Station with configuration.

**Parameters:**

- `config` (StationConfig): Station configuration object containing:
  - `station_id` (str): Unique identifier for the station
  - `station_name` (str): Display name for the station
  - `allowed_licenses` (List[str]): List of allowed content licenses
  - `enable_blockchain` (bool): Enable blockchain trust network
  - `enable_edge_optimization` (bool): Enable edge device optimization
  - `trust_threshold` (float): Minimum trust score for content (0.0-1.0)
  - `max_playlist_size` (int): Maximum number of tracks in a playlist
  - `streaming_quality` (str): Default streaming quality tier

**Returns:** None

**Raises:** None on construction (validation occurs in config)

**Example:**

```python
from qfzz.core.station import QFZZStation
from qfzz.core.config import StationConfig

# Create configuration
config = StationConfig(
    station_id="qfzz_station_001",
    station_name="MyRadio",
    allowed_licenses=["CC-BY", "CC-BY-SA"],
    enable_blockchain=True,
    enable_edge_optimization=True,
    trust_threshold=0.6,
    max_playlist_size=100,
    streaming_quality="high"
)

# Initialize station
station = QFZZStation(config)
```

---

## Core Methods

### start()

```python
def start(self) -> None
```

Start the radio station and initialize all components.

**Parameters:** None

**Returns:** None

**Raises:**
- `RuntimeError`: If station is already running

**Side Effects:**
- Sets `_running` to True
- Initializes PersonalizedDJ
- Initializes DatasetManager
- Initializes MusicPlayer
- Optionally initializes BlockchainTrustNetwork
- Optionally initializes EdgeOptimizer
- Logs initialization messages

**Example:**

```python
station.start()
print(f"Station running: {station.is_running()}")  # True
```

---

### stop()

```python
def stop(self) -> None
```

Stop the radio station and cleanup all components.

**Parameters:** None

**Returns:** None

**Raises:**
- `RuntimeError`: If station is not running

**Side Effects:**
- Sets `_running` to False
- Releases all component resources
- Clears listener connections
- Logs cleanup messages

**Example:**

```python
station.stop()
print(f"Station running: {station.is_running()}")  # False
```

---

### is_running()

```python
def is_running(self) -> bool
```

Check if the station is currently running.

**Parameters:** None

**Returns:** bool - True if running, False otherwise

**Example:**

```python
if station.is_running():
    print("Station is active")
else:
    print("Station is inactive")
```

---

## Listener Management

### add_listener()

```python
def add_listener(self, user_id: str, preferences: Optional[Dict[str, Any]] = None) -> None
```

Add a new listener to the station.

**Parameters:**

- `user_id` (str): Unique identifier for the listener
- `preferences` (Optional[Dict[str, Any]]): Optional listener preferences including:
  - `genres` (Dict[str, float]): Genre preferences with weights
  - `artists` (Dict[str, float]): Artist preferences with weights
  - `energy_level` (float): Preferred energy level (0.0-1.0)
  - `discovery_factor` (float): Willingness to discover new music (0.0-1.0)

**Returns:** None

**Raises:**
- `RuntimeError`: If station is not running
- `ValueError`: If user_id is invalid

**Side Effects:**
- Adds listener to internal registry
- Initializes listener state with connection timestamp
- Logs listener addition

**Example:**

```python
# Add listener without preferences
station.add_listener("user_001")

# Add listener with preferences
station.add_listener("user_002", preferences={
    "genres": {"rock": 0.8, "pop": 0.6},
    "artists": {"Beatles": 0.9, "Pink Floyd": 0.7},
    "energy_level": 0.7,
    "discovery_factor": 0.4
})
```

---

### remove_listener()

```python
def remove_listener(self, user_id: str) -> None
```

Remove a listener from the station.

**Parameters:**

- `user_id` (str): User identifier to remove

**Returns:** None

**Raises:**
- `ValueError`: If user not found

**Side Effects:**
- Removes listener from internal registry
- Clears listener's playlist and state
- Logs listener removal

**Example:**

```python
station.remove_listener("user_001")
```

---

## Playlist Generation

### generate_playlist()

```python
def generate_playlist(self, user_id: str) -> List[Dict[str, Any]]
```

Generate a personalized playlist for a specific listener.

**Parameters:**

- `user_id` (str): User identifier

**Returns:** List[Dict[str, Any]] - List of recommended track dictionaries with:
  - `track_id` (str): Track identifier
  - `title` (str): Track title
  - `artist` (str): Artist name
  - `genre` (str): Music genre
  - `energy` (float): Energy level
  - `mood` (str): Track mood
  - `duration` (int): Duration in seconds
  - Additional track metadata

**Raises:**
- `RuntimeError`: If station is not running
- `ValueError`: If user is not a listener

**Side Effects:**
- Calls PersonalizedDJ for recommendations
- Filters by trust scores if blockchain is enabled
- Stores playlist in listener state
- Logs playlist generation

**Filtering Logic:**

1. DJ generates recommendations based on user profile
2. If blockchain is enabled: Filters by `trust_threshold`
3. Limits to `max_playlist_size` tracks
4. Returns filtered playlist

**Example:**

```python
station.add_listener("user_001")
playlist = station.generate_playlist("user_001")

for track in playlist[:5]:
    print(f"{track['title']} by {track['artist']}")
```

---

## Interaction Recording

### record_interaction()

```python
def record_interaction(self, user_id: str, track_id: str, 
                      interaction_type: str, rating: Optional[float] = None) -> None
```

Record user interaction with a track for preference learning.

**Parameters:**

- `user_id` (str): User identifier
- `track_id` (str): Track identifier
- `interaction_type` (str): Type of interaction:
  - `"play"`: User played the track
  - `"skip"`: User skipped the track
  - `"like"`: User liked the track
  - `"dislike"`: User disliked the track
  - `"favorite"`: User marked as favorite
- `rating` (Optional[float]): Optional explicit rating (0.0-1.0)

**Returns:** None

**Raises:**
- `RuntimeError`: If station is not running
- `ValueError`: If user is not a listener

**Side Effects:**
- Records feedback in DJ's user profile
- Updates user preferences based on feedback
- Adjusts genre, artist, and mood weights
- Logs interaction

**Feedback Strength:**

- `"like"`: +0.1 weight
- `"dislike"`: -0.1 weight
- `"skip"`: -0.05 weight
- `"play"`: +0.05 weight
- `"favorite"`: +0.2 weight
- Rating: (rating - 0.5) * 0.2

**Example:**

```python
# Record basic interactions
station.record_interaction("user_001", "track_123", "play")
station.record_interaction("user_001", "track_456", "skip")
station.record_interaction("user_001", "track_789", "like")

# Record with explicit rating
station.record_interaction("user_001", "track_101", "play", rating=0.9)
```

---

## Statistics

### get_station_stats()

```python
def get_station_stats(self) -> Dict[str, Any]
```

Get comprehensive statistics about the station.

**Parameters:** None

**Returns:** Dict[str, Any] containing:
- `station_id` (str): Station identifier
- `station_name` (str): Station name
- `running` (bool): Is station running
- `listener_count` (int): Number of connected listeners
- `blockchain_enabled` (bool): Blockchain support enabled
- `edge_optimization_enabled` (bool): Edge optimization enabled
- `trust_threshold` (float): Trust score threshold
- `streaming_quality` (str): Default quality tier

**Example:**

```python
stats = station.get_station_stats()
print(f"Active listeners: {stats['listener_count']}")
print(f"Station: {stats['station_name']}")
print(f"Blockchain: {stats['blockchain_enabled']}")
```

---

## Code Examples

### Complete Workflow Example

```python
from qfzz.core.station import QFZZStation
from qfzz.core.config import StationConfig

# 1. Create configuration
config = StationConfig(
    station_id="jazz_radio_001",
    station_name="Jazz Night Radio",
    allowed_licenses=["CC-BY", "CC-BY-SA", "CC0"],
    enable_blockchain=True,
    enable_edge_optimization=True,
    trust_threshold=0.65,
    max_playlist_size=50,
    streaming_quality="high"
)

# 2. Initialize and start station
station = QFZZStation(config)
station.start()

# 3. Add multiple listeners
listeners = [
    ("user_alice", {"genres": {"jazz": 0.9, "blues": 0.7}}),
    ("user_bob", {"genres": {"jazz": 0.8, "classical": 0.6}}),
    ("user_charlie", {"genres": {"jazz": 0.7, "funk": 0.8}})
]

for user_id, prefs in listeners:
    station.add_listener(user_id, preferences=prefs)

# 4. Generate playlists
for user_id, _ in listeners:
    playlist = station.generate_playlist(user_id)
    print(f"\nPlaylist for {user_id}:")
    for track in playlist[:3]:
        print(f"  - {track['title']} by {track['artist']}")

# 5. Simulate user interactions
station.record_interaction("user_alice", "track_0001", "play")
station.record_interaction("user_alice", "track_0002", "like")
station.record_interaction("user_alice", "track_0003", "skip")
station.record_interaction("user_bob", "track_0005", "favorite", rating=0.95)

# 6. Get updated stats
stats = station.get_station_stats()
print(f"\nStation Stats:")
print(f"  Running: {stats['running']}")
print(f"  Listeners: {stats['listener_count']}")
print(f"  Blockchain: {stats['blockchain_enabled']}")

# 7. Cleanup
station.stop()
```

### Dynamic Listener Management

```python
# Add listener
station.add_listener("user_dynamic")

# Generate initial playlist
initial_playlist = station.generate_playlist("user_dynamic")
print(f"Initial: {len(initial_playlist)} tracks")

# User provides feedback
for i in range(min(5, len(initial_playlist))):
    track = initial_playlist[i]
    if i % 2 == 0:
        station.record_interaction("user_dynamic", track['track_id'], "like")
    else:
        station.record_interaction("user_dynamic", track['track_id'], "skip")

# Generate new playlist with learned preferences
updated_playlist = station.generate_playlist("user_dynamic")
print(f"Updated: {len(updated_playlist)} tracks")

# Remove listener
station.remove_listener("user_dynamic")
```

### Trust-Based Filtering Example

```python
# With blockchain enabled
config = StationConfig(
    station_id="trusted_radio",
    station_name="Verified Content Radio",
    enable_blockchain=True,
    trust_threshold=0.75,  # Only high-trust content
    max_playlist_size=30
)

station = QFZZStation(config)
station.start()

station.add_listener("trusted_user")

# Generated playlist will only include tracks
# where trust_score >= 0.75
playlist = station.generate_playlist("trusted_user")
print(f"All tracks meet trust threshold: 0.75")
print(f"Returned {len(playlist)} trusted tracks")

station.stop()
```

---

## Error Handling

### Common Error Scenarios

**Station Not Running:**

```python
station = QFZZStation(config)
# Forgot to call start()

try:
    station.generate_playlist("user_001")
except RuntimeError as e:
    print(f"Error: {e}")  # "Station is not running"
```

**User Not Listener:**

```python
station.start()
try:
    station.generate_playlist("unknown_user")
except ValueError as e:
    print(f"Error: {e}")  # "User unknown_user is not a listener"
```

**Listener Already Added:**

```python
station.add_listener("user_001")
station.add_listener("user_001")  # Silently overwrites with fresh state
```

---

## Implementation Details

### Component Initialization

Components are initialized lazily when `start()` is called:

```python
def _initialize_components(self) -> None:
    from qfzz.dj.personalized_dj import PersonalizedDJ
    from qfzz.datasets.manager import DatasetManager
    from qfzz.streaming.player import MusicPlayer
    
    self._dj = PersonalizedDJ()
    self._dataset_manager = DatasetManager(
        allowed_licenses=self.config.allowed_licenses
    )
    self._player = MusicPlayer()
    
    if self.config.enable_blockchain:
        from qfzz.blockchain.trust_network import BlockchainTrustNetwork
        self._trust_network = BlockchainTrustNetwork()
    
    if self.config.enable_edge_optimization:
        from qfzz.edge.optimizer import EdgeOptimizer
        self._edge_optimizer = EdgeOptimizer()
```

### Playlist Filtering

The playlist generation applies multi-stage filtering:

1. **DJ Recommendations**: Get initial recommendations from PersonalizedDJ
2. **Trust Filtering** (if enabled): Filter by blockchain trust scores
3. **Size Limiting**: Truncate to `max_playlist_size`
4. **State Storage**: Store playlist in listener state

### Listener State Structure

```python
{
    'user_id': str,
    'preferences': Dict[str, Any],
    'connected_at': ISO-8601 timestamp,
    'playlist': List[Dict[str, Any]]
}
```

---

## Best Practices

1. **Always call `start()` before operations**: Ensure components are initialized
2. **Manage listener lifecycle**: Remove listeners when disconnected to free memory
3. **Record interactions for accuracy**: More feedback = better recommendations
4. **Monitor statistics**: Use `get_station_stats()` to track station health
5. **Handle exceptions**: Wrap operations in try-except for robust error handling
6. **Use appropriate trust thresholds**: Balance content quality with diversity
7. **Consider edge devices**: Enable optimization for better mobile experience

---

## Related Classes

- **StationConfig**: Configuration class for station setup
- **PersonalizedDJ**: Handles recommendation generation
- **DatasetManager**: Manages music content datasets
- **BlockchainTrustNetwork**: Provides trust verification (optional)
- **EdgeOptimizer**: Optimizes for edge devices (optional)
- **MusicPlayer**: Handles audio streaming

---

## Version Information

- **Module**: `qfzz.core.station`
- **Class**: `QFZZStation`
- **Python**: 3.8+
- **Dependencies**: logging, typing, datetime

