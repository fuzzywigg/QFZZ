# PersonalizedDJ: Agentic AI for Music

The `PersonalizedDJ` is QFZZ's intelligent recommendation engine that learns your musical preferences and creates tailored playlists.

## Overview

Unlike traditional recommendation systems that rely solely on collaborative filtering, QFZZ's PersonalizedDJ combines multiple approaches:

- **Content-based filtering**: Analyzes track attributes
- **Collaborative signals**: Learns from user behavior patterns
- **Agentic AI**: Autonomous decision-making for discovery
- **Real-time adaptation**: Responds immediately to feedback

## Key Features

### 🎯 Multi-Dimensional Taste Profiling

The DJ builds a comprehensive profile of your musical taste:

```python
class UserProfile:
    genres: Dict[str, float]          # Genre preferences with weights
    artists: Dict[str, float]         # Artist preferences
    moods: Dict[str, float]          # Mood preferences
    energy_level: float              # Preferred energy level (0.0-1.0)
    tempo_preference: str            # slow, medium, fast, or varied
    discovery_factor: float          # Exploration vs. exploitation (0.0-1.0)
    interactions: List[Dict]         # Full interaction history
```

### 🔍 Intelligent Discovery

Balance familiarity with exploration:

```python
station.add_listener(
    user_id="alice",
    preferences={
        'genres': {'rock': 0.8, 'indie': 0.6},
        'discovery_factor': 0.2  # 20% new/unexpected tracks
    }
)
```

**Discovery Factor Guide**:
- `0.0`: Only familiar content (no exploration)
- `0.2`: Mostly familiar with some discovery (recommended)
- `0.5`: Equal balance
- `0.8`: Mostly discovery with some familiar
- `1.0`: Complete exploration (random)

### 🎨 Mood and Energy Matching

Fine-tune recommendations by mood and energy:

```python
preferences = {
    'energy_level': 0.7,  # 0.0 = calm, 1.0 = energetic
    'moods': {
        'upbeat': 0.8,
        'mellow': 0.3
    },
    'tempo_preference': 'fast'  # slow, medium, fast, varied
}
```

### 🧠 Learning from Feedback

The DJ learns from both implicit and explicit signals:

**Implicit Feedback**:
```python
# User plays track (positive signal: +0.05)
station.record_interaction(user_id, track_id, "play")

# User skips track (negative signal: -0.05)
station.record_interaction(user_id, track_id, "skip")
```

**Explicit Feedback**:
```python
# User likes track (positive signal: +0.1)
station.record_interaction(user_id, track_id, "like")

# User favorites track (strong positive: +0.2)
station.record_interaction(user_id, track_id, "favorite")

# User rates track (scaled: -0.1 to +0.1)
station.record_interaction(user_id, track_id, "rate", rating=0.8)
```

## How It Works

### 1. Profile Creation

When a user first connects:

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ()

# Create profile with initial preferences
profile = dj.get_or_create_profile(
    user_id="bob",
    initial_preferences={
        'genres': {'jazz': 0.9, 'blues': 0.7},
        'artists': {'Miles Davis': 0.9},
        'energy_level': 0.4,
        'discovery_factor': 0.15
    }
)
```

### 2. Track Scoring Algorithm

Each track is scored based on multiple factors:

```python
def calculate_track_score(track, profile):
    score = 0.0

    # Genre matching (30% weight)
    if track['genre'] in profile.genres:
        score += profile.genres[track['genre']] * 0.3
    elif track['genre'] in similar_genres(profile.genres):
        score += 0.5 * 0.3  # Partial match for similar genres

    # Artist matching (25% weight)
    if track['artist'] in profile.artists:
        score += profile.artists[track['artist']] * 0.25

    # Energy level matching (20% weight)
    energy_diff = abs(track['energy'] - profile.energy_level)
    score += (1.0 - energy_diff) * 0.2

    # Tempo matching (15% weight)
    if track['tempo'] == profile.tempo_preference or profile.tempo_preference == 'varied':
        score += 0.15

    # Mood matching (10% weight)
    if track['mood'] in profile.moods:
        score += profile.moods[track['mood']] * 0.1

    return score
```

**Scoring Breakdown**:

| Factor | Weight | Description |
|--------|--------|-------------|
| Genre | 30% | Direct genre match or similarity |
| Artist | 25% | Known artist preference |
| Energy | 20% | Energy level compatibility |
| Tempo | 15% | Tempo preference match |
| Mood | 10% | Mood compatibility |

### 3. Discovery Application

After scoring, apply discovery factor:

```python
def apply_discovery(scored_tracks, discovery_factor):
    # Split into familiar and discovery pools
    split_point = int(len(scored_tracks) * (1.0 - discovery_factor))

    # Take high-scoring tracks
    familiar = scored_tracks[:split_point]

    # Add random discovery tracks
    discovery_pool = scored_tracks[split_point:]
    num_discovery = int(len(familiar) * discovery_factor / (1.0 - discovery_factor))
    discovery = random.sample(discovery_pool, min(num_discovery, len(discovery_pool)))

    return [track for _, track in familiar] + [track for _, track in discovery]
```

### 4. Continuous Learning

Preferences update incrementally with each interaction:

```python
def update_from_feedback(profile, track, interaction_type, rating):
    # Calculate feedback strength
    strength = FEEDBACK_STRENGTH[interaction_type]

    # Update genre preference
    if 'genre' in track:
        current = profile.genres.get(track['genre'], 0.5)
        new_weight = clamp(current + strength, 0.0, 1.0)
        profile.genres[track['genre']] = new_weight

    # Similarly for artists, moods, etc.
```

## Genre Similarity Mapping

The DJ understands genre relationships:

```python
genre_similarity = {
    'rock': ['alternative', 'indie', 'punk', 'metal'],
    'pop': ['dance', 'electronic', 'indie-pop', 'synth-pop'],
    'jazz': ['blues', 'soul', 'funk', 'swing'],
    'classical': ['orchestral', 'baroque', 'romantic', 'contemporary'],
    'hip-hop': ['rap', 'trap', 'r&b', 'urban'],
    'electronic': ['techno', 'house', 'trance', 'ambient'],
    'folk': ['acoustic', 'country', 'americana', 'singer-songwriter'],
    'metal': ['hard-rock', 'progressive', 'death-metal', 'black-metal']
}
```

This enables:
- Discovery of related genres
- Expansion of musical horizons
- Natural progression in tastes

## Advanced Usage

### Custom Content Catalog

Add your own music catalog:

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ()

# Add custom tracks
my_tracks = [
    {
        'track_id': 'custom_001',
        'title': 'Moonlight Sonata',
        'artist': 'Beethoven',
        'genre': 'classical',
        'mood': 'contemplative',
        'energy': 0.3,
        'tempo': 'slow',
        'duration': 900,
        'content_id': 'beethoven_moonlight',
        'creator_id': 'beethoven'
    },
    # ... more tracks
]

dj.add_content(my_tracks)
```

### Access User Profile

Inspect and analyze user preferences:

```python
# Get profile
profile = dj.get_profile("user_id")

if profile:
    print(f"Top genres: {sorted(profile.genres.items(), key=lambda x: x[1], reverse=True)[:3]}")
    print(f"Top artists: {sorted(profile.artists.items(), key=lambda x: x[1], reverse=True)[:3]}")
    print(f"Energy level: {profile.energy_level}")
    print(f"Discovery factor: {profile.discovery_factor}")
    print(f"Total interactions: {len(profile.interactions)}")
```

### Adjust Discovery Over Time

Dynamically adjust discovery based on user maturity:

```python
# New user: Higher discovery
if len(profile.interactions) < 50:
    profile.discovery_factor = 0.3
# Established user: Lower discovery
elif len(profile.interactions) > 500:
    profile.discovery_factor = 0.1
# Regular user: Balanced
else:
    profile.discovery_factor = 0.2
```

### Context-Aware Recommendations

Adapt recommendations to context:

```python
import datetime

def get_time_of_day_preferences():
    hour = datetime.datetime.now().hour

    if 6 <= hour < 12:  # Morning
        return {'energy_level': 0.6, 'moods': {'upbeat': 0.8}}
    elif 12 <= hour < 18:  # Afternoon
        return {'energy_level': 0.7, 'moods': {'energetic': 0.7}}
    elif 18 <= hour < 22:  # Evening
        return {'energy_level': 0.5, 'moods': {'mellow': 0.7}}
    else:  # Night
        return {'energy_level': 0.3, 'moods': {'calm': 0.8}}

# Use context in recommendations
context_prefs = get_time_of_day_preferences()
playlist = station.generate_playlist(user_id)
```

## Best Practices

### 1. Provide Initial Preferences

Help the DJ bootstrap:

```python
# Good: Provide initial preferences
station.add_listener(
    user_id="user",
    preferences={
        'genres': {'rock': 0.7, 'indie': 0.6},
        'artists': {'Radiohead': 0.9, 'Arcade Fire': 0.8}
    }
)

# Suboptimal: Empty preferences (cold start)
station.add_listener(user_id="user")
```

### 2. Balance Discovery Factor

Too low = echo chamber, too high = chaos:

```python
# Too low: Repetitive
preferences = {'discovery_factor': 0.05}

# Recommended: Balanced
preferences = {'discovery_factor': 0.2}

# Too high: Random
preferences = {'discovery_factor': 0.9}
```

### 3. Provide Rich Feedback

More feedback = better recommendations:

```python
# Good: Rich feedback
station.record_interaction(user_id, track_id, "play")
station.record_interaction(user_id, track_id, "like")
station.record_interaction(user_id, track_id, "favorite")

# Better: With ratings
station.record_interaction(user_id, track_id, "rate", rating=0.85)
```

### 4. Regular Profile Analysis

Monitor profile evolution:

```python
def analyze_profile(profile):
    """Analyze user profile for insights."""

    # Genre diversity
    genre_count = len(profile.genres)
    top_genre_weight = max(profile.genres.values()) if profile.genres else 0

    # Artist diversity
    artist_count = len(profile.artists)

    # Interaction patterns
    interaction_count = len(profile.interactions)
    recent_interactions = profile.interactions[-20:] if len(profile.interactions) >= 20 else profile.interactions

    likes = sum(1 for i in recent_interactions if i['type'] == 'like')
    skips = sum(1 for i in recent_interactions if i['type'] == 'skip')

    return {
        'genre_diversity': genre_count,
        'genre_concentration': top_genre_weight,
        'artist_diversity': artist_count,
        'total_interactions': interaction_count,
        'recent_like_rate': likes / len(recent_interactions) if recent_interactions else 0,
        'recent_skip_rate': skips / len(recent_interactions) if recent_interactions else 0
    }
```

## Performance Optimization

### Caching

Profiles are cached in memory:
- O(1) lookup time
- No disk I/O for hot profiles
- Incremental updates

### Efficient Scoring

Track scoring is vectorized where possible:
- Pre-compute genre similarities
- Batch profile lookups
- Lazy track loading

### Memory Management

Profiles persist in memory but can be persisted:

```python
def save_profile(profile, path):
    """Save profile to disk."""
    import pickle
    with open(path, 'wb') as f:
        pickle.dump(profile, f)

def load_profile(path):
    """Load profile from disk."""
    import pickle
    with open(path, 'rb') as f:
        return pickle.load(f)
```

## Future Enhancements

See [Roadmap](../roadmap.md) for planned features:

- [ ] Deep learning recommendation models
- [ ] Audio feature extraction and embedding
- [ ] Context-aware recommendations (time, location, activity)
- [ ] Reinforcement learning for long-term satisfaction
- [ ] Multi-armed bandit algorithms
- [ ] Active learning for efficient preference elicitation
- [ ] Cross-user collaborative filtering
- [ ] Session-based recommendation

## Research Background

The PersonalizedDJ incorporates techniques from:

- **Music Information Retrieval (MIR)**: Genre classification, similarity
- **Recommendation Systems**: Collaborative and content-based filtering
- **Multi-Armed Bandits**: Exploration-exploitation trade-off
- **Reinforcement Learning**: Long-term reward optimization

For detailed research analysis, see [Research Section](../research/gaps-analysis.md).

---

**Next**: [Blockchain Trust →](quantum-security.md) | [API Reference →](../api-reference/dj.md)
