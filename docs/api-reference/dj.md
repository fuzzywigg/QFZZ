# PersonalizedDJ and UserProfile API Reference

## Overview

The DJ module provides AI-powered personalized music recommendations through the `PersonalizedDJ` class and user preference management via the `UserProfile` class. The system learns user preferences through interactions and generates tailored playlists using multi-factor scoring algorithms that consider genres, artists, energy levels, tempos, and moods.

## Table of Contents

- [PersonalizedDJ Class](#personalizeddj-class)
  - [Constructor](#constructor)
  - [Profile Management](#profile-management)
  - [Recommendations](#recommendations)
  - [Feedback Recording](#feedback-recording)
  - [Content Management](#content-management)
- [UserProfile Class](#userprofile-class)
  - [Constructor](#constructor-1)
  - [Preference Updates](#preference-updates)
  - [Interaction History](#interaction-history)
  - [Profile Retrieval](#profile-retrieval)
- [Code Examples](#code-examples)
- [Algorithm Details](#algorithm-details)

---

## PersonalizedDJ Class

### Constructor

```python
def __init__(self) -> None
```

Initialize the Personalized DJ system.

**Parameters:** None

**Returns:** None

**Side Effects:**
- Initializes empty user profiles dictionary
- Initializes empty content catalog
- Sets up genre similarity mappings
- Logs initialization

**Example:**

```python
from qfzz.dj.personalized_dj import PersonalizedDJ

dj = PersonalizedDJ()
```

**Genre Similarity Mappings:**

The DJ maintains predefined genre similarity relationships:

- **rock**: alternative, indie, punk, metal
- **pop**: dance, electronic, indie-pop, synth-pop
- **jazz**: blues, soul, funk, swing
- **classical**: orchestral, baroque, romantic, contemporary
- **hip-hop**: rap, trap, r&b, urban
- **electronic**: techno, house, trance, ambient
- **folk**: acoustic, country, americana, singer-songwriter
- **metal**: hard-rock, progressive, death-metal, black-metal

---

## Profile Management

### get_or_create_profile()

```python
def get_or_create_profile(self, user_id: str,
                         initial_preferences: Optional[Dict[str, Any]] = None) -> UserProfile
```

Get an existing user profile or create a new one.

**Parameters:**

- `user_id` (str): Unique user identifier
- `initial_preferences` (Optional[Dict[str, Any]]): Optional initial preferences:
  - `genres` (Dict[str, float]): Genre preferences {genre: weight}
  - `artists` (Dict[str, float]): Artist preferences {artist: weight}
  - `energy_level` (float): Preferred energy (0.0-1.0)
  - `discovery_factor` (float): Discovery openness (0.0-1.0)

**Returns:** UserProfile - Existing or newly created profile

**Raises:**
- `ValueError`: If preferences contain invalid values

**Side Effects:**
- Creates new profile if doesn't exist
- Applies initial preferences
- Caches profile in `_user_profiles`
- Logs profile creation

**Example:**

```python
# Get or create with no preferences
profile1 = dj.get_or_create_profile("user_001")

# Get or create with initial preferences
profile2 = dj.get_or_create_profile("user_002", {
    "genres": {
        "rock": 0.8,
        "indie": 0.7,
        "pop": 0.5
    },
    "artists": {
        "The Beatles": 0.9,
        "Pink Floyd": 0.85
    },
    "energy_level": 0.7,
    "discovery_factor": 0.3
})

# Second call returns cached profile
profile2_again = dj.get_or_create_profile("user_002")
assert profile2 is profile2_again
```

---

### get_profile()

```python
def get_profile(self, user_id: str) -> Optional[UserProfile]
```

Get an existing user profile without creating if missing.

**Parameters:**

- `user_id` (str): User identifier

**Returns:** UserProfile if exists, None otherwise

**Example:**

```python
profile = dj.get_profile("user_001")
if profile:
    print(f"Profile exists for {profile.user_id}")
else:
    print("Profile not found")
```

---

## Recommendations

### recommend()

```python
def recommend(self, user_id: str, preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]
```

Generate personalized recommendations for a user.

**Parameters:**

- `user_id` (str): User identifier
- `preferences` (Optional[Dict[str, Any]]): Optional real-time preferences to override profile

**Returns:** List[Dict[str, Any]] - List of recommended tracks with metadata

**Raises:**
- `ValueError`: If user_id is invalid

**Side Effects:**
- Creates user profile if doesn't exist
- Scores all candidate tracks
- Applies discovery factor
- Logs recommendations

**Recommendation Process:**

1. **Get/Create Profile**: Fetch user profile with optional preferences override
2. **Gather Candidates**: Retrieve track candidates from catalog or generate samples
3. **Score Tracks**: Calculate compatibility score for each track (0.0-1.0)
4. **Sort Results**: Rank by score descending
5. **Apply Discovery**: Introduce serendipity based on discovery_factor
6. **Return**: Final recommendation list

**Track Score Factors:**

| Factor | Weight | Description |
|--------|--------|-------------|
| Genre Matching | 30% | Exact match: 100% of weight, Similar genre: 50% |
| Artist | 25% | User's preferred artists |
| Energy Level | 20% | Matching energy level with penalty for difference |
| Tempo | 15% | Matching tempo preference |
| Mood | 10% | Matching mood preference |

**Example:**

```python
# Basic recommendation
recommendations = dj.recommend("user_001")
print(f"Recommended {len(recommendations)} tracks")

for track in recommendations[:5]:
    print(f"  {track['title']} by {track['artist']}")

# Recommendation with real-time preferences
preferences = {
    "genres": {"jazz": 0.9, "blues": 0.7},
    "energy_level": 0.4,  # Lower energy mood
    "discovery_factor": 0.5
}
relaxed_recs = dj.recommend("user_001", preferences)
```

---

## Feedback Recording

### record_feedback()

```python
def record_feedback(self, user_id: str, track_id: str,
                   interaction_type: str, rating: Optional[float] = None) -> None
```

Record user feedback to improve recommendations.

**Parameters:**

- `user_id` (str): User identifier
- `track_id` (str): Track identifier
- `interaction_type` (str): Interaction type:
  - `"play"`: User played track
  - `"skip"`: User skipped track
  - `"like"`: User liked track
  - `"dislike"`: User disliked track
  - `"favorite"`: User marked as favorite
- `rating` (Optional[float]): Explicit rating (0.0-1.0)

**Returns:** None

**Raises:**
- `ValueError`: If user_id invalid or rating out of range

**Side Effects:**
- Creates profile if doesn't exist
- Adds interaction to profile history
- Updates genre, artist, and mood preferences
- Recalculates trust scores

**Feedback Strength (Weight Change):**

| Type | Strength |
|------|----------|
| favorite | +0.2 |
| like | +0.1 |
| play | +0.05 |
| skip | -0.05 |
| dislike | -0.1 |
| rating | (rating - 0.5) × 0.2 |

**Example:**

```python
# Record basic feedback
dj.record_feedback("user_001", "track_001", "play")
dj.record_feedback("user_001", "track_002", "like")
dj.record_feedback("user_001", "track_003", "skip")
dj.record_feedback("user_001", "track_004", "dislike")
dj.record_feedback("user_001", "track_005", "favorite")

# Record with explicit rating
dj.record_feedback("user_001", "track_006", "play", rating=0.95)
dj.record_feedback("user_001", "track_007", "play", rating=0.2)

# View updated profile
profile = dj.get_profile("user_001")
print(f"Interaction history: {len(profile.interaction_history)} entries")
```

---

## Content Management

### add_content()

```python
def add_content(self, tracks: List[Dict[str, Any]]) -> None
```

Add tracks to the content catalog.

**Parameters:**

- `tracks` (List[Dict[str, Any]]): List of track dictionaries with required fields:
  - `track_id` (str): Unique track identifier
  - `title` (str): Track title
  - `artist` (str): Artist name
  - `genre` (str): Music genre
  - `mood` (str): Track mood
  - `energy` (float): Energy level (0.0-1.0)
  - `tempo` (str): Tempo (slow, medium, fast)
  - `duration` (int): Duration in seconds

**Returns:** None

**Side Effects:**
- Extends internal content catalog
- Logs catalog update

**Example:**

```python
new_tracks = [
    {
        "track_id": "trk_001",
        "title": "Moonlight Sonata",
        "artist": "Ludwig van Beethoven",
        "album": "Piano Sonatas",
        "genre": "classical",
        "mood": "calm",
        "energy": 0.3,
        "tempo": "slow",
        "duration": 480,
        "content_id": "content_001",
        "creator_id": "creator_001"
    },
    {
        "track_id": "trk_002",
        "title": "Take Five",
        "artist": "Dave Brubeck Quartet",
        "album": "Time Out",
        "genre": "jazz",
        "mood": "upbeat",
        "energy": 0.7,
        "tempo": "medium",
        "duration": 324,
        "content_id": "content_002",
        "creator_id": "creator_002"
    }
]

dj.add_content(new_tracks)
```

---

## UserProfile Class

### Constructor

```python
@dataclass
class UserProfile:
    user_id: str
    genres: Dict[str, float] = field(default_factory=dict)
    artists: Dict[str, float] = field(default_factory=dict)
    moods: Dict[str, float] = field(default_factory=dict)
    energy_level: float = 0.5
    tempo_preference: str = 'medium'
    discovery_factor: float = 0.3
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

Create a user profile for personalized recommendations.

**Parameters:**

- `user_id` (str): Unique user identifier
- `genres` (Dict[str, float]): Genre weights (0.0-1.0), default empty
- `artists` (Dict[str, float]): Artist weights (0.0-1.0), default empty
- `moods` (Dict[str, float]): Mood weights (0.0-1.0), default empty
- `energy_level` (float): Preferred energy (0.0-1.0), default 0.5
- `tempo_preference` (str): Preferred tempo (slow/medium/fast/varied), default 'medium'
- `discovery_factor` (float): Discovery openness (0.0-1.0), default 0.3
- `interaction_history` (List): Interaction records, default empty
- `created_at` (str): ISO-8601 timestamp
- `updated_at` (str): ISO-8601 timestamp

**Raises:** ValueError if validation fails

**Example:**

```python
from qfzz.dj.profiles import UserProfile

# Create with defaults
profile1 = UserProfile(user_id="user_001")

# Create with custom preferences
profile2 = UserProfile(
    user_id="user_002",
    genres={"rock": 0.8, "indie": 0.6},
    artists={"The Beatles": 0.9},
    energy_level=0.7,
    tempo_preference="fast",
    discovery_factor=0.5
)
```

---

## Preference Updates

### update_genre_preference()

```python
def update_genre_preference(self, genre: str, weight: float) -> None
```

Update weight for a music genre.

**Parameters:**

- `genre` (str): Genre name
- `weight` (float): Preference weight (0.0-1.0)

**Returns:** None

**Raises:**
- `ValueError`: If weight not in range [0.0, 1.0]

**Side Effects:**
- Updates genre weight
- Sets `updated_at` timestamp

**Example:**

```python
profile = dj.get_or_create_profile("user_001")
profile.update_genre_preference("jazz", 0.9)
profile.update_genre_preference("blues", 0.7)
profile.update_genre_preference("pop", 0.4)
```

---

### update_artist_preference()

```python
def update_artist_preference(self, artist: str, weight: float) -> None
```

Update weight for an artist.

**Parameters:**

- `artist` (str): Artist name
- `weight` (float): Preference weight (0.0-1.0)

**Returns:** None

**Raises:**
- `ValueError`: If weight not in range [0.0, 1.0]

**Side Effects:**
- Updates artist weight
- Sets `updated_at` timestamp

**Example:**

```python
profile.update_artist_preference("Miles Davis", 0.95)
profile.update_artist_preference("John Coltrane", 0.85)
```

---

### update_mood_preference()

```python
def update_mood_preference(self, mood: str, weight: float) -> None
```

Update weight for a mood.

**Parameters:**

- `mood` (str): Mood name (e.g., "upbeat", "calm", "energetic")
- `weight` (float): Preference weight (0.0-1.0)

**Returns:** None

**Raises:**
- `ValueError`: If weight not in range [0.0, 1.0]

**Side Effects:**
- Updates mood weight
- Sets `updated_at` timestamp

**Example:**

```python
profile.update_mood_preference("calm", 0.8)
profile.update_mood_preference("upbeat", 0.6)
profile.update_mood_preference("energetic", 0.4)
```

---

## Interaction History

### add_interaction()

```python
def add_interaction(self, interaction: Dict[str, Any]) -> None
```

Add an interaction to user history.

**Parameters:**

- `interaction` (Dict[str, Any]): Interaction details:
  - `track_id` (str): Track identifier
  - `type` (str): Interaction type
  - `rating` (Optional[float]): Rating value
  - `timestamp` (str): ISO-8601 timestamp (auto-generated)

**Returns:** None

**Side Effects:**
- Appends interaction to history
- Updates `updated_at` timestamp
- Trims history to last 1000 entries

**Example:**

```python
profile.add_interaction({
    "track_id": "track_001",
    "type": "like",
    "rating": 0.9
})

print(f"Interactions: {len(profile.interaction_history)}")
```

---

## Profile Retrieval

### get_top_genres()

```python
def get_top_genres(self, limit: int = 5) -> List[str]
```

Get top preferred genres.

**Parameters:**

- `limit` (int): Maximum genres to return, default 5

**Returns:** List[str] - Genre names sorted by preference (highest first)

**Example:**

```python
profile = dj.get_or_create_profile("user_001", {
    "genres": {
        "rock": 0.9,
        "indie": 0.8,
        "pop": 0.6,
        "jazz": 0.5,
        "classical": 0.3
    }
})

top_genres = profile.get_top_genres(3)
print(top_genres)  # ['rock', 'indie', 'pop']
```

---

### get_top_artists()

```python
def get_top_artists(self, limit: int = 10) -> List[str]
```

Get top preferred artists.

**Parameters:**

- `limit` (int): Maximum artists to return, default 10

**Returns:** List[str] - Artist names sorted by preference (highest first)

**Example:**

```python
profile.update_artist_preference("The Beatles", 0.95)
profile.update_artist_preference("Pink Floyd", 0.90)
profile.update_artist_preference("David Bowie", 0.85)

top_artists = profile.get_top_artists(2)
print(top_artists)  # ['The Beatles', 'Pink Floyd']
```

---

### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

Convert profile to dictionary representation.

**Parameters:** None

**Returns:** Dict with all profile attributes

**Example:**

```python
profile_dict = profile.to_dict()
print(profile_dict)
# {
#     'user_id': 'user_001',
#     'genres': {'rock': 0.9, ...},
#     'artists': {'The Beatles': 0.95, ...},
#     'energy_level': 0.7,
#     'discovery_factor': 0.3,
#     'interaction_history': [...],
#     'created_at': '2024-01-15T10:30:00',
#     'updated_at': '2024-01-15T10:35:00'
# }
```

---

### validate()

```python
def validate(self) -> None
```

Validate profile parameters.

**Parameters:** None

**Returns:** None

**Raises:**
- `ValueError`: If any parameter invalid

**Validation Rules:**

- `user_id`: Must be non-empty
- `energy_level`: Must be 0.0-1.0
- `tempo_preference`: Must be 'slow', 'medium', 'fast', or 'varied'
- `discovery_factor`: Must be 0.0-1.0

**Example:**

```python
try:
    profile = UserProfile(
        user_id="",  # Invalid!
        energy_level=0.5
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Code Examples

### Complete DJ Workflow

```python
from qfzz.dj.personalized_dj import PersonalizedDJ

# Initialize DJ
dj = PersonalizedDJ()

# Create profiles with initial preferences
dj.get_or_create_profile("alice", {
    "genres": {"jazz": 0.9, "blues": 0.8, "soul": 0.7},
    "energy_level": 0.4,
    "discovery_factor": 0.2
})

dj.get_or_create_profile("bob", {
    "genres": {"rock": 0.9, "indie": 0.8},
    "energy_level": 0.8,
    "discovery_factor": 0.5
})

# Add content catalog
sample_tracks = [
    {
        "track_id": f"track_{i:04d}",
        "title": f"Track {i}",
        "artist": f"Artist {i % 5}",
        "genre": ["jazz", "blues", "rock", "pop"][i % 4],
        "mood": ["calm", "upbeat", "energetic", "mellow"][i % 4],
        "energy": (i % 10) / 10.0,
        "tempo": ["slow", "medium", "fast"][i % 3],
        "duration": 200 + (i % 100) * 2,
        "content_id": f"content_{i:04d}",
        "creator_id": f"creator_{i % 3}"
    }
    for i in range(100)
]
dj.add_content(sample_tracks)

# Generate recommendations
print("=== Alice's Recommendations ===")
alice_recs = dj.recommend("alice")
for track in alice_recs[:3]:
    print(f"  {track['title']} ({track['genre']}, energy: {track['energy']:.1f})")

print("\n=== Bob's Recommendations ===")
bob_recs = dj.recommend("bob")
for track in bob_recs[:3]:
    print(f"  {track['title']} ({track['genre']}, energy: {track['energy']:.1f})")

# Record feedback
dj.record_feedback("alice", alice_recs[0]['track_id'], "like", rating=0.9)
dj.record_feedback("alice", alice_recs[1]['track_id'], "skip")
dj.record_feedback("bob", bob_recs[0]['track_id'], "favorite")

# Check updated profiles
alice_profile = dj.get_profile("alice")
print(f"\n=== Alice's Profile ===")
print(f"Top genres: {alice_profile.get_top_genres(3)}")
print(f"Interactions: {len(alice_profile.interaction_history)}")
```

### Learning from Feedback

```python
# Initial recommendations without feedback
initial = dj.recommend("new_user")

# User provides feedback
for i, track in enumerate(initial[:10]):
    if track['genre'] == 'jazz':
        dj.record_feedback("new_user", track['track_id'], "like")
    elif track['genre'] == 'rock':
        dj.record_feedback("new_user", track['track_id'], "skip")
    else:
        dj.record_feedback("new_user", track['track_id'], "play")

# Updated recommendations should favor jazz
updated = dj.recommend("new_user")
profile = dj.get_profile("new_user")
print(f"Learned genres: {profile.get_top_genres()}")
```

---

## Algorithm Details

### Recommendation Scoring Algorithm

```
Final Score = (Genre × 0.30) + (Artist × 0.25) + (Energy × 0.20) +
              (Tempo × 0.15) + (Mood × 0.10)

Where:
  Genre: 1.0 if exact match, 0.5 if similar, 0.0 if no match
  Artist: Profile weight if artist in preferences, 0.0 otherwise
  Energy: 1.0 - |track_energy - profile_energy|
  Tempo: 1.0 if matches preference, 0.0 otherwise
  Mood: Profile weight if mood in preferences, 0.0 otherwise
```

### Discovery Factor Application

The discovery factor introduces serendipity while maintaining relevance:

1. Split tracks into two groups:
   - High-scoring: (1.0 - discovery_factor) of tracks
   - Discovery pool: discovery_factor of tracks
2. Include all high-scoring tracks
3. Randomly sample from discovery pool based on factor
4. Shuffle results

Lower discovery factor = more predictable recommendations
Higher discovery factor = more serendipitous recommendations

---

## Version Information

- **Module**: `qfzz.dj.personalized_dj`, `qfzz.dj.profiles`
- **Classes**: `PersonalizedDJ`, `UserProfile`
- **Python**: 3.8+
- **Dependencies**: dataclasses, typing, datetime, random, logging
