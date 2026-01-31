# Music Logic - QFZZ FuzzyRadio

## Core Principles

### 1. Flow Over Randomness

Tracks should flow naturally, not just shuffle randomly. Consider:
- **Energy levels**: Gradual transitions, not jarring jumps
- **Key/tempo compatibility**: Musical harmony between tracks
- **Thematic connections**: Genre, era, mood, instrumentation
- **Narrative arc**: Build and release tension throughout programming

### 2. Discovery Over Familiarity

Balance the known with the unknown:
- **70% familiar**: Tracks most listeners will recognize or appreciate
- **20% adjacent**: Similar to favorites but less known
- **10% surprise**: Wild cards that expand horizons

### 3. Context Matters

Consider:
- **Time of day**: Morning energy vs late night introspection
- **Day of week**: Monday motivation vs Friday celebration
- **Season**: Summer anthems vs winter warmth
- **Listener mood**: Read the room via requests and interaction

## Track Selection Algorithm

### Priority Levels (0-10)

**10**: Emergency request, listener celebration, special moment
**8-9**: Strong listener request, perfect for current mood
**6-7**: Good fit for current flow, strong track
**4-5**: Solid choice, could play anytime
**2-3**: Filler, use when nothing else fits
**0-1**: Skip unless desperate

### Selection Factors

1. **Last played**: Don't repeat tracks within 4 hours
2. **Artist diversity**: Vary artists, don't play same artist twice in 2 hours
3. **Genre balance**: Don't cluster too many similar tracks
4. **Energy curve**: Build, sustain, or release energy intentionally
5. **Listener requests**: Weight heavily but not exclusively

### Decision Tree

```
START: Need next track

1. Check for high-priority requests (priority >= 8)
   YES → Validate fit → Select
   NO → Continue

2. Analyze current flow
   - What's the energy level?
   - What genre/mood are we in?
   - Where should we go next?

3. Filter available tracks
   - Remove recently played (< 4 hours)
   - Remove same artist (< 2 hours)
   - Remove poor flow fits (energy/genre/tempo mismatch)

4. Score remaining tracks
   - Flow fit: 0-40 points
   - Listener preference: 0-30 points
   - Diversity bonus: 0-20 points
   - Time-appropriate: 0-10 points

5. Select highest scoring track
   - If tie, choose most requested
   - If still tie, random selection

6. Log selection reasoning to dj_memory.json
```

## Genre Management

### Genre Categories

**Primary Genres**:
- Jazz (Bebop, Cool, Fusion, Smooth)
- Rock (Classic, Indie, Alternative, Progressive)
- Electronic (House, Techno, Ambient, Downtempo)
- Hip-Hop (Boom Bap, Trap, Conscious, Experimental)
- Soul/R&B (Classic Soul, Neo-Soul, Contemporary R&B)
- Pop (Indie Pop, Art Pop, Synth Pop)
- Folk (Traditional, Contemporary, Singer-Songwriter)

**Mood Tags**:
- Energetic, Mellow, Melancholic, Uplifting
- Aggressive, Peaceful, Romantic, Contemplative
- Nostalgic, Futuristic, Raw, Polished

### Cross-Genre Transitions

**Natural Bridges**:
- Jazz → Soul (shared instrumentation, groove)
- Electronic → Hip-Hop (beats, production style)
- Indie Rock → Folk (acoustic elements, storytelling)
- Ambient → Jazz (atmospheric, improvisational)

**Transitional Tracks**:
Maintain a list of "bridge" tracks that work across multiple genres:
- Fusion jazz with electronic elements
- Hip-hop with live instrumentation
- Electronic music with organic textures
- Rock with extended ambient sections

## Tempo & Energy Management

### Energy Levels (1-10)

**1-2**: Ambient, drone, very sparse
**3-4**: Mellow, downtempo, chill
**5-6**: Moderate, conversational, balanced
**7-8**: Upbeat, energetic, engaging
**9-10**: High energy, dance-ready, intense

### Energy Flow Patterns

**Morning Ramp** (6am-10am):
```
Start: 3 → Gradual rise → Peak: 7-8 by 9am
```

**Midday Sustain** (10am-3pm):
```
Maintain: 6-8, occasional dips to 5 for variety
```

**Afternoon Coast** (3pm-7pm):
```
Start: 7 → Gradual decline → End: 5-6
```

**Evening Wind Down** (7pm-midnight):
```
Start: 5-6 → Gradual decline → End: 3-4
```

**Late Night Ambient** (midnight-6am):
```
Maintain: 2-4, deep contemplation
```

### Tempo Guidelines

**BPM Ranges**:
- Very Slow: < 80 BPM (ballads, ambient)
- Slow: 80-100 BPM (downtempo, soul)
- Moderate: 100-120 BPM (midtempo, funk)
- Upbeat: 120-140 BPM (pop, rock, dance)
- Fast: 140+ BPM (uptempo dance, punk)

**Transitions**:
- ±20 BPM: Smooth, barely noticeable
- ±40 BPM: Noticeable but acceptable
- >40 BPM: Needs DJ acknowledgment or bridge track

## Playlist Queue Management

### Queue Structure

```
PLAYING NOW: Current track
↓
NEXT UP (positions 1-3): High confidence, good flow
↓
COMING SOON (positions 4-10): Flexible, can be reordered
↓
BACKLOG (positions 11+): Low priority, future consideration
```

### Dynamic Reordering

**Triggers for reordering**:
1. New high-priority request
2. Energy mismatch detected
3. Genre clustering (too many similar tracks)
4. Artist repetition risk
5. Listener feedback (explicit or implicit)

**Reordering Logic**:
- Preserve NEXT UP if flow is good
- Bump high-priority requests to position 2-3
- Spread out similar genres across queue
- Maintain overall energy arc

### Emergency Fallbacks

**If queue empties**:
1. Check recent successful patterns in dj_memory.json
2. Select from diverse "safe" tracks (proven performers)
3. Build new queue based on current time/mood
4. Log incident for learning

## Listener Preference Learning

### Tracking Engagement

**Implicit Signals**:
- Listening duration (stayed vs left)
- Request patterns (genres, artists, moods)
- Time of day preferences
- Response to DJ interactions

**Explicit Signals**:
- Direct requests
- Shoutouts and messages
- Positive/negative reactions
- Follows and shares

### Preference Storage

Store in `listener_state.json`:
```json
{
  "preferences": {
    "genres": {
      "jazz": 45,
      "electronic": 30,
      "soul": 25
    },
    "moods": {
      "mellow": 60,
      "energetic": 40
    },
    "time_preferences": {
      "morning": ["jazz", "electronic"],
      "evening": ["soul", "ambient"]
    }
  }
}
```

### Applying Preferences

- Weight track selection toward preferred genres
- Adjust energy levels to match typical listener mood
- Time-appropriate programming based on historical data
- Never 100% preference-driven (maintain DJ personality)

## Special Programming

### Themed Blocks

**Monday Morning Jazz**:
- 100% jazz (but varied: bebop, cool, fusion)
- Energy: 4-7, building through block
- Focus: Smooth start to week

**Friday Night Dance Party**:
- Electronic, funk, dance-oriented rock
- Energy: 7-9 throughout
- Focus: Weekend celebration

**Sunday Chill Sessions**:
- Ambient, downtempo, acoustic
- Energy: 2-5, very mellow
- Focus: Relaxation and reflection

### Event-Driven Programming

**New releases**: Feature when available, but not forced
**Anniversaries**: Note significant album/artist milestones
**Seasonal**: Adjust mood for weather and season
**Listener milestones**: Celebrate community moments

## Metadata & Context

### Required Track Metadata

```json
{
  "track_id": "unique_id",
  "title": "Track Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "year": 2023,
  "genre": ["primary", "secondary"],
  "mood": ["tag1", "tag2"],
  "energy": 7,
  "tempo": 120,
  "duration": 240,
  "last_played": "ISO8601_timestamp",
  "play_count": 42,
  "skip_count": 2,
  "tags": ["atmospheric", "guitar-driven"]
}
```

### Context Enrichment

For each track, maintain:
- **Story**: Interesting fact or anecdote
- **Connection**: Related artists or tracks
- **Moment**: When/why to play this track
- **Intro ideas**: Potential DJ intros

Store in separate knowledge base, reference by track_id.

## Quality Control

### Track Inclusion Criteria

**Must have**:
- Clean audio quality (no compression artifacts)
- Proper metadata (artist, title, year minimum)
- Appropriate content (no explicit content without warning)
- Licensing clearance (free/licensed/public domain only)

**Nice to have**:
- Album art
- Full metadata (album, genre, mood tags)
- Context/story information
- Related track suggestions

### Exclusion Rules

**Never play**:
- Tracks with poor audio quality
- Duplicate versions without reason
- Tracks with licensing issues
- Content that violates community standards

**Warn before playing**:
- Explicit lyrics (rare, but announce if necessary)
- Unusual/challenging content
- Very long tracks (>15 minutes)

## Performance Metrics

### Track Performance

Track for each song:
- **Play count**: How often played
- **Skip rate**: Percentage of incomplete listens
- **Request count**: How often requested
- **Context success**: When it works best (time, mood, genre)

### Programming Success

Measure overall station performance:
- **Average listening duration**: Goal >30 minutes
- **Peak concurrent listeners**: Track growth
- **Request volume**: More requests = more engagement
- **Genre diversity**: Maintain balanced programming

### Optimization

Use metrics to:
- Phase out consistently skipped tracks
- Increase rotation of successful tracks
- Identify best times for different genres
- Refine energy flow patterns

---

**Remember**: This is music logic, not rigid rules. The DJ's intuition and personality should always guide final decisions.
