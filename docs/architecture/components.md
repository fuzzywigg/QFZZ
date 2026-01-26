# Component Details

This document provides detailed information about each QFZZ component, including design decisions, implementation details, and usage patterns.

## QFZZStation (Orchestrator)

### Overview

The `QFZZStation` is the central coordinator for all QFZZ functionality. It manages component lifecycle, user sessions, and coordinates interactions between components.

### Design Decisions

**Why an orchestrator pattern?**
- Centralized control reduces complexity
- Easy to add new components
- Clear ownership of user sessions
- Simplified configuration management

**Lazy initialization**
- Components created only when needed
- Reduces startup time
- Allows conditional feature enablement
- Minimizes resource usage

### Implementation Details

```python
class QFZZStation:
    def __init__(self, config: StationConfig):
        self.config = config
        self._running = False
        self._listeners: Dict[str, Any] = {}

        # Components initialized lazily
        self._dj = None
        self._dataset_manager = None
        self._trust_network = None
        self._edge_optimizer = None
        self._player = None
```

### Component Initialization

Components are initialized in `_initialize_components()`:

```python
def _initialize_components(self) -> None:
    # Always initialized
    self._dj = PersonalizedDJ()
    self._dataset_manager = DatasetManager(
        allowed_licenses=self.config.allowed_licenses
    )
    self._player = MusicPlayer()

    # Conditional initialization
    if self.config.enable_blockchain:
        self._trust_network = BlockchainTrustNetwork()

    if self.config.enable_edge_optimization:
        self._edge_optimizer = EdgeOptimizer()
```

### State Management

The station maintains listener state:

```python
self._listeners[user_id] = {
    'user_id': user_id,
    'preferences': preferences,
    'connected_at': timestamp,
    'playlist': []
}
```

### Key Methods

#### `start()` and `stop()`

Manage station lifecycle:
- Start: Initialize components, set running flag
- Stop: Cleanup components, clear state

#### `add_listener()` and `remove_listener()`

Manage user sessions:
- Add: Create listener record with preferences
- Remove: Clean up listener state

#### `generate_playlist()`

Orchestrate playlist generation:
1. Get user preferences
2. Request recommendations from DJ
3. Filter by trust threshold (if blockchain enabled)
4. Limit to max playlist size
5. Store and return playlist

#### `record_interaction()`

Process user feedback:
1. Validate user exists
2. Record with DJ for learning
3. Update blockchain trust (if enabled)

### Configuration

Station behavior controlled by `StationConfig`:

```python
@dataclass
class StationConfig:
    station_name: str
    station_id: str = field(default_factory=lambda: f"qfzz_{uuid.uuid4().hex[:8]}")
    enable_blockchain: bool = False
    enable_edge_optimization: bool = False
    max_playlist_size: int = 20
    trust_threshold: float = 0.5
    streaming_quality: str = "high"
    allowed_licenses: List[str] = field(default_factory=lambda: ['CC-BY', 'CC-BY-SA', 'CC0'])
```

### Error Handling

Station validates state before operations:

```python
if not self._running:
    raise RuntimeError("Station is not running")

if user_id not in self._listeners:
    raise ValueError(f"User {user_id} is not a listener")
```

---

## PersonalizedDJ (AI Layer)

### Overview

The `PersonalizedDJ` is an AI-powered recommendation engine that learns user preferences and generates personalized playlists.

### Design Decisions

**Multi-dimensional profiling**
- Genre preferences with weights
- Artist preferences
- Mood and energy preferences
- Tempo preferences
- Discovery factor for exploration

**Implicit and explicit feedback**
- Implicit: plays, skips
- Explicit: likes, ratings
- Combined for comprehensive learning

**Genre similarity mapping**
- Predefined genre relationships
- Enables discovery of similar music
- Expands recommendation space

### User Profile Structure

```python
class UserProfile:
    user_id: str
    genres: Dict[str, float]  # genre -> weight
    artists: Dict[str, float]  # artist -> weight
    moods: Dict[str, float]  # mood -> weight
    energy_level: float  # 0.0-1.0
    tempo_preference: str  # slow, medium, fast, varied
    discovery_factor: float  # 0.0-1.0
    interactions: List[Dict]  # interaction history
```

### Recommendation Algorithm

#### Step 1: Get Candidate Tracks

```python
def _get_candidate_tracks(self, profile: UserProfile) -> List[Dict]:
    # Use catalog if available, otherwise generate samples
    if self._content_catalog:
        return self._content_catalog
    return self._generate_sample_tracks(profile)
```

#### Step 2: Score Each Track

Scoring algorithm weights multiple factors:

```python
def _calculate_track_score(self, track, profile, preferences) -> float:
    score = 0.0

    # Genre matching (30%)
    if track['genre'] in profile.genres:
        score += profile.genres[track['genre']] * 0.3
    elif track['genre'] in similar_genres:
        score += 0.5 * 0.3

    # Artist matching (25%)
    if track['artist'] in profile.artists:
        score += profile.artists[track['artist']] * 0.25

    # Energy level matching (20%)
    energy_diff = abs(track['energy'] - profile.energy_level)
    score += (1.0 - energy_diff) * 0.2

    # Tempo matching (15%)
    if track['tempo'] == profile.tempo_preference:
        score += 0.15

    # Mood matching (10%)
    if track['mood'] in profile.moods:
        score += profile.moods[track['mood']] * 0.1

    return score
```

#### Step 3: Apply Discovery Factor

```python
def _apply_discovery(self, scored_tracks, discovery_factor) -> List[Dict]:
    # Split into high-scoring and discovery candidates
    split_point = int(len(scored_tracks) * (1.0 - discovery_factor))

    high_scores = scored_tracks[:split_point]
    discovery_pool = scored_tracks[split_point:]

    # Combine with random discovery tracks
    recommendations = [track for _, track in high_scores]

    if discovery_pool:
        num_discovery = int(len(recommendations) * discovery_factor / (1.0 - discovery_factor))
        discovery_tracks = random.sample(discovery_pool, min(num_discovery, len(discovery_pool)))
        recommendations.extend([track for _, track in discovery_tracks])

    return recommendations
```

### Feedback Processing

#### Recording Feedback

```python
def record_feedback(self, user_id, track_id, interaction_type, rating):
    profile = self.get_or_create_profile(user_id)

    interaction = {
        'track_id': track_id,
        'type': interaction_type,
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    }
    profile.add_interaction(interaction)

    self._update_profile_from_feedback(profile, track_id, interaction_type, rating)
```

#### Updating Preferences

```python
def _update_profile_from_feedback(self, profile, track_id, interaction_type, rating):
    # Find track
    track = self._find_track(track_id)
    if not track:
        return

    # Calculate feedback strength
    strength = {
        'like': 0.1,
        'dislike': -0.1,
        'skip': -0.05,
        'play': 0.05,
        'favorite': 0.2
    }.get(interaction_type, 0.0)

    # Apply to preferences
    if 'genre' in track:
        current = profile.genres.get(track['genre'], 0.5)
        profile.genres[track['genre']] = max(0.0, min(1.0, current + strength))

    # Similarly for artists, moods, etc.
```

### Genre Similarity

Predefined mappings for genre exploration:

```python
genre_similarity = {
    'rock': ['alternative', 'indie', 'punk', 'metal'],
    'pop': ['dance', 'electronic', 'indie-pop', 'synth-pop'],
    'jazz': ['blues', 'soul', 'funk', 'swing'],
    'classical': ['orchestral', 'baroque', 'romantic', 'contemporary'],
    'hip-hop': ['rap', 'trap', 'r&b', 'urban'],
    'electronic': ['techno', 'house', 'trance', 'ambient'],
    # ... more mappings
}
```

---

## DatasetManager (Data Layer)

### Overview

The `DatasetManager` handles music dataset management with comprehensive quality scoring and license validation.

### Quality Scoring

#### Multi-Factor Quality Assessment

Quality score calculated from five factors:

1. **Metadata Completeness (30%)**
   - Required fields: title, artist, genre, duration
   - Optional fields: album, year, mood, energy, tempo

2. **Data Consistency (25%)**
   - Field presence consistency across tracks
   - Valid value ranges
   - Data type consistency

3. **Dataset Size (20%)**
   - Logarithmic scoring based on track count
   - 100+ tracks = good dataset

4. **Diversity (15%)**
   - Genre variety
   - Artist distribution
   - Encourages diverse content

5. **License Permissiveness (10%)**
   - Commercial use allowed
   - Derivative works allowed
   - Share-alike requirement

#### Implementation

```python
def calculate_quality_score(self, dataset: Dataset) -> float:
    score = 0.0

    # Metadata completeness
    metadata_score = self._score_metadata_completeness(dataset)
    score += metadata_score * 0.3

    # Data consistency
    consistency_score = self._score_data_consistency(dataset)
    score += consistency_score * 0.25

    # Dataset size
    size_score = self._score_dataset_size(dataset)
    score += size_score * 0.2

    # Diversity
    diversity_score = self._score_diversity(dataset)
    score += diversity_score * 0.15

    # License permissiveness
    license_score = self._score_license(dataset.license)
    score += license_score * 0.1

    return score
```

### License Validation

#### Supported Licenses

- **CC-BY**: Attribution required
- **CC-BY-SA**: Attribution + Share-alike
- **CC0**: Public domain
- **Custom**: User-defined licenses

#### License Compatibility

```python
def validate_license(self, license: DatasetLicense) -> bool:
    return license.is_compatible_with(self._allowed_licenses)
```

### Dataset Model

```python
@dataclass
class Dataset:
    dataset_id: str
    name: str
    description: str
    source: str
    license: DatasetLicense
    tracks: List[Dict[str, Any]] = field(default_factory=list)
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## BlockchainTrustNetwork (Security Layer)

### Overview

The `BlockchainTrustNetwork` provides immutable content verification using blockchain technology.

### Block Structure

```python
@dataclass
class Block:
    index: int
    timestamp: str
    records: List[TrustRecord]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
```

### Trust Record

```python
@dataclass
class TrustRecord:
    record_id: str
    content_id: str
    creator_id: str
    trust_score: float
    verifications: int = 0
    reports: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Proof-of-Work Mining

```python
def mine_block(self, difficulty: int) -> None:
    target = "0" * difficulty

    while not self.hash.startswith(target):
        self.nonce += 1
        self.hash = self.calculate_hash()
```

### Trust Score Calculation

```python
def calculate_trust_score(self) -> float:
    if self.verifications + self.reports == 0:
        return 0.5  # Neutral default

    return self.verifications / (self.verifications + self.reports)
```

### Chain Validation

```python
def is_chain_valid(self) -> bool:
    for i in range(1, len(self._chain)):
        current = self._chain[i]
        previous = self._chain[i - 1]

        # Verify hash
        if not current.is_valid():
            return False

        # Verify linkage
        if current.previous_hash != previous.hash:
            return False

    return True
```

---

## EdgeOptimizer (Optimization Layer)

### Overview

The `EdgeOptimizer` adapts streaming parameters for different devices and network conditions.

### Device Configuration

```python
@dataclass
class EdgeDeviceConfig:
    device_id: str
    device_type: DeviceType
    network_type: NetworkType
    bandwidth_mbps: float
    cpu_cores: int
    ram_gb: float
    storage_mb: float
    battery_powered: bool
    battery_level: float
    supports_hardware_decode: bool
    max_bitrate_kbps: int
```

### Optimization Profiles

Four built-in profiles:

```python
profiles = {
    'power_save': {
        'max_quality': 'medium',
        'buffer_multiplier': 1.5,
        'enable_hardware_decode': True,
        'aggressive_cache': True,
        'max_bitrate_kbps': 128
    },
    'balanced': {...},
    'quality': {...},
    'bandwidth_save': {...}
}
```

### Optimization Algorithm

```python
def optimize_streaming(self, device_id, preferences) -> Dict:
    device = self._devices[device_id]

    # Select profile
    profile = self._select_profile(device, preferences)

    # Calculate parameters
    quality = self._calculate_quality(device, profile, preferences)
    bitrate = self._calculate_bitrate(device, profile, quality)
    buffer_size = self._calculate_buffer_size(device, profile)
    cache_settings = self._calculate_cache_settings(device, profile)

    return {
        'profile': profile_name,
        'quality': quality,
        'bitrate_kbps': bitrate,
        'buffer_size_seconds': buffer_size,
        'cache_enabled': cache_settings['enabled'],
        'cache_size_mb': cache_settings['size_mb']
    }
```

### Profile Selection Logic

```python
def _select_profile(self, device, preferences):
    # User preference takes priority
    if preferences and 'profile' in preferences:
        return preferences['profile']

    # Auto-select based on conditions
    if device.battery_powered and device.battery_level < 0.3:
        return 'power_save'

    if device.network_type in [NetworkType.CELLULAR_3G, NetworkType.CELLULAR_4G]:
        return 'bandwidth_save'

    if device.bandwidth_mbps < 1.0:
        return 'bandwidth_save'

    if device.bandwidth_mbps >= 5.0 and device.device_type in [DeviceType.DESKTOP]:
        return 'quality'

    return 'balanced'
```

---

## MusicPlayer (Streaming Layer)

### Overview

The `MusicPlayer` manages audio streaming and playback.

### Key Responsibilities

- Stream initialization
- Playback control (play, pause, stop, skip)
- Buffer management
- Quality adaptation
- Error recovery

### Implementation Notes

The current implementation provides interfaces for:

```python
class MusicPlayer:
    def play(track_id, streaming_params) -> None
    def pause() -> None
    def stop() -> None
    def skip() -> None
    def set_volume(level) -> None
    def get_playback_state() -> Dict
```

Integration with actual streaming services (Spotify, YouTube Music, etc.) is planned for future releases.

---

## Component Interactions

### Typical Request Flow

1. **User connects**: Station creates listener record
2. **Playlist requested**: Station → DJ → Dataset → Blockchain → User
3. **User provides feedback**: User → Station → DJ → Profile update
4. **Trust updated**: User → Station → Blockchain → Trust recalculation

### Component Dependencies

```
Station (orchestrator)
├── PersonalizedDJ (required)
├── DatasetManager (required)
├── MusicPlayer (required)
├── BlockchainTrustNetwork (optional)
└── EdgeOptimizer (optional)
```

---

## Extension Points

Each component can be extended or replaced:

1. **Custom DJ Algorithm**: Subclass `PersonalizedDJ`
2. **Alternative Storage**: Implement dataset repository interface
3. **Different Consensus**: Replace blockchain implementation
4. **Custom Profiles**: Add optimization profiles
5. **Streaming Backend**: Integrate with services

---

**Next**: [Data Flow →](data-flow.md) | [API Reference →](../api-reference/station.md)
