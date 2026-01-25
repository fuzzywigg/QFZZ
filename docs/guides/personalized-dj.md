# PersonalizedDJ System Guide

This guide covers the PersonalizedDJ system in QFZZ, an AI agent that learns your music preferences and provides personalized curation and interaction.

## Table of Contents

1. [Overview](#overview)
2. [How the DJ Learns Your Preferences](#how-the-dj-learns-your-preferences)
3. [User Profile System](#user-profile-system)
4. [Trust Building](#trust-building)
5. [Conversation Context](#conversation-context)
6. [Music Recommendation Logic](#music-recommendation-logic)
7. [Community Connections](#community-connections)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)

## Overview

The PersonalizedDJ is an AI agent that serves as your personal radio DJ, learning your music taste over time and building a trusted relationship. Unlike generic recommendation systems, your DJ:

- **Remembers** your interactions and preferences
- **Learns** what you like through conversations
- **Adapts** to your mood and context
- **Builds trust** through consistent interactions
- **Connects** you with a community of music lovers

See the [DJ API Documentation](../api/dj.md) for detailed API reference.

### Key Features

- 🎵 **Personalized Music Curation** - Recommendations based on your unique taste
- 💬 **Conversational Interaction** - Natural dialogue about music
- 🤝 **Trust Building** - Relationship grows over time
- 🌍 **Community of Trust** - Connect with like-minded music lovers
- 📱 **Edge Device Support** - Runs locally on your device
- 🔒 **Privacy First** - Your data stays with you

## How the DJ Learns Your Preferences

The PersonalizedDJ uses multiple signals to understand your music taste:

### 1. Explicit Preference Updates

You can directly tell the DJ what you like:

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# User explicitly shares preferences
dj.update_preferences(
    user_id="user_001",
    preferences=["jazz", "electronic", "ambient", "downtempo"]
)

# These preferences are immediately reflected in recommendations
response = dj.interact("user_001", "Recommend something for me")
print(response)
# Output: "Based on your taste for jazz, electronic, ambient, 
#          I've got the perfect track queued up!"
```

### 2. Conversational Learning

The DJ learns from your conversations:

```python
# User expresses mood
response1 = dj.interact("user_001", "I'm feeling really happy and energetic today!")
# DJ learns: user is in energetic mood
# DJ responds: "I love that energy! Let me bring up the tempo with some uplifting beats!"

# User requests genre
response2 = dj.interact("user_001", "Play some chill jazz")
# DJ learns: user likes jazz, currently wants chill music

# User gives feedback
response3 = dj.interact("user_001", "This track is perfect!")
# DJ learns: current recommendation style is working
```

### 3. Interaction Patterns

The DJ tracks patterns over time:

- **Time of day**: Morning vs evening preferences
- **Session length**: Quick picks vs long listening sessions
- **Skip patterns**: What gets skipped reveals dislikes
- **Replay requests**: What gets repeated reveals favorites

### 4. Community Influences

Learn from your music community:

```python
# Connect with friends who share your taste
dj.add_to_community("user_001", "friend_002")
dj.add_to_community("user_001", "friend_003")

# DJ can now consider community preferences:
# "Your friend Alex has been loving this new album, want to check it out?"
```

## User Profile System

Each user has a detailed profile that evolves over time.

### UserProfile Structure

```python
from qfzz.dj import UserProfile
from datetime import datetime

# Profile is created automatically on first interaction
profile = UserProfile(
    user_id="user_001",
    name="Alex",
    music_preferences=["jazz", "electronic"],
    interaction_history=[],
    trust_score=0.5,  # Starts at 0.5
    community_connections=[],
    created_at=datetime.now()
)
```

### Profile Attributes

**user_id** (str)
- Unique identifier for the user
- Used to retrieve profile and track history
- Should be persistent across sessions

**name** (str)
- Display name for personalized greetings
- Used in DJ responses
- Makes interaction more personal

**music_preferences** (List[str])
- List of genres, styles, artists, moods
- Grows over time through interactions
- Used for recommendation filtering

**interaction_history** (List[Dict])
- Complete history of DJ interactions
- Each entry includes: timestamp, message, type
- Used to understand context and patterns

**trust_score** (float, 0.0-1.0)
- Measures relationship strength
- Starts at 0.5 (neutral)
- Increases with positive interactions (+0.01 per interaction)
- Affects DJ's confidence in recommendations

**community_connections** (List[str])
- User IDs of connected friends
- Enables social music discovery
- Builds trust network

**created_at** (datetime)
- Profile creation timestamp
- Used to calculate relationship duration
- Helps personalize greetings ("We've been together for 3 months!")

### Profile Evolution

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Day 1: New user
greeting = dj.greet_user("user_001", "Alex")
print(greeting)
# "Hey Alex! Welcome to QFZZ! I'm DJ Quantum, your personal DJ. 
#  Let's discover some great music together!"

# After 50 interactions
greeting = dj.greet_user("user_001", "Alex")
print(greeting)
# "Welcome back, Alex! Great to see you again. 
#  We've shared 50 sessions together. What's your vibe today?"

# Check profile status
profile = dj.user_profiles["user_001"]
print(f"Trust score: {profile.trust_score:.2f}")  # 0.95
print(f"Preferences: {len(profile.music_preferences)}")  # 12 genres
print(f"Interactions: {len(profile.interaction_history)}")  # 100 messages
print(f"Community: {len(profile.community_connections)}")  # 5 friends
```

## Trust Building

Trust is central to the PersonalizedDJ system. It represents the strength of the relationship between user and DJ.

### Trust Score Mechanics

**Initial Trust**: 0.5 (neutral)

**Building Trust**: +0.01 per positive interaction

**Trust Levels**:
- **0.0-0.3**: Stranger - Generic recommendations
- **0.3-0.5**: Acquaintance - Basic personalization
- **0.5-0.7**: Friend - Good personalization
- **0.7-0.9**: Close Friend - Great personalization
- **0.9-1.0**: Best Friend - Perfect personalization

### How Trust Affects Recommendations

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Low trust (0.5) - Generic response
dj.greet_user("new_user", "Sam")
response = dj.interact("new_user", "Recommend something")
print(response)
# "I'm learning your taste! Let's start with something smooth. 
#  Tell me what genres you're into?"

# After many interactions - trust builds
for i in range(50):
    dj.interact("new_user", f"Message {i}")

trust = dj.get_trust_score("new_user")
print(f"Trust: {trust:.2f}")  # 0.95

# High trust (0.95) - Confident personalized response
response = dj.interact("new_user", "Recommend something")
print(response)
# "Based on your taste for jazz, electronic, ambient, 
#  I've got the perfect track queued up! Let me play something special for you."
```

### Trust and Privacy

Trust is built through interaction, not surveillance:

- ✅ **DO**: Increase trust through positive interactions
- ✅ **DO**: Let users control their data
- ✅ **DO**: Respect privacy in recommendations
- ❌ **DON'T**: Track users without consent
- ❌ **DON'T**: Share user data with others
- ❌ **DON'T**: Make assumptions without interaction

### Checking Trust Score

```python
# Get user's trust score
trust_score = dj.get_trust_score("user_001")

if trust_score < 0.5:
    print("Building relationship...")
elif trust_score < 0.7:
    print("Good relationship established")
elif trust_score < 0.9:
    print("Strong relationship")
else:
    print("Excellent relationship")
```

## Conversation Context

The DJ maintains conversation context to provide coherent, contextual responses.

### Context Tracking

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Context builds across messages
dj.interact("user_001", "I'm in a great mood today!")
# Context: [user is happy]

dj.interact("user_001", "Play something uplifting")
# Context: [user is happy, wants uplifting music]

dj.interact("user_001", "Maybe some electronic music?")
# Context: [user is happy, wants uplifting electronic music]

# DJ can now make highly contextual recommendation
```

### Context Storage

Context is stored per user:

```python
# Each user has separate conversation context
dj.conversation_context = {
    "user_001": [
        "I'm in a great mood today!",
        "Play something uplifting",
        "Maybe some electronic music?"
    ],
    "user_002": [
        "Feeling a bit down",
        "Need some comfort music"
    ]
}

# Context helps DJ understand current request
```

### Interaction History

Complete interaction history is stored in the user profile:

```python
profile = dj.user_profiles["user_001"]

# View interaction history
for interaction in profile.interaction_history[-5:]:  # Last 5
    timestamp = interaction['timestamp']
    message = interaction['message']
    msg_type = interaction['type']  # 'user_message' or 'dj_response'
    print(f"[{timestamp}] ({msg_type}): {message}")

# Example output:
# [2024-01-15 10:30:00] (user_message): I'm in a great mood today!
# [2024-01-15 10:30:01] (dj_response): I love that energy! Let me bring up...
# [2024-01-15 10:31:15] (user_message): Play something uplifting
# [2024-01-15 10:31:16] (dj_response): Based on your taste for electronic...
```

### Context-Aware Responses

The DJ uses context to generate better responses:

```python
def demonstrate_context_awareness():
    dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)
    
    # Without context
    r1 = dj.interact("user_001", "Play something")
    print(r1)  # Generic: "I'm learning your taste!"
    
    # Build context
    dj.update_preferences("user_001", ["jazz", "electronic"])
    dj.interact("user_001", "I'm feeling energetic")
    
    # With context - much better response
    r2 = dj.interact("user_001", "Play something")
    print(r2)  # Contextual: "Based on your taste for jazz, electronic, 
               #              and your energetic vibe, here's a perfect track!"
```

## Music Recommendation Logic

The DJ uses a multi-factor recommendation system:

### Recommendation Factors

1. **Explicit Preferences** - Genres and styles you've stated
2. **Mood Context** - Current emotional state
3. **Listening History** - Past interaction patterns
4. **Time Context** - Time of day, day of week
5. **Community Influence** - What similar users enjoy

### Basic Recommendation Flow

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# 1. Update user preferences
dj.update_preferences("user_001", ["jazz", "electronic", "ambient"])

# 2. User requests music
response = dj.interact("user_001", "Play some music for me")
print(response)
# "Based on your taste for jazz, electronic, ambient, 
#  I've got the perfect track queued up!"

# 3. DJ generates recommendation based on:
#    - Preferences: ["jazz", "electronic", "ambient"]
#    - Mood: (detected from conversation)
#    - History: (past preferences)
#    - Trust: (high trust = more confident recommendations)
```

### Mood-Based Recommendations

The DJ detects mood from conversation:

```python
# Energetic mood
response = dj.interact("user_001", "I'm so happy and excited today!")
print(response)
# "I love that energy! Let me bring up the tempo with some uplifting beats!"
# DJ will recommend: high-tempo, energetic tracks

# Calm mood
response = dj.interact("user_001", "I need to relax and chill")
print(response)
# "I hear you. Let me create a calming atmosphere with some mellow vibes."
# DJ will recommend: low-tempo, ambient tracks

# Sad mood
response = dj.interact("user_001", "Feeling a bit down today")
print(response)
# "I hear you. Let me create a calming atmosphere with some mellow vibes."
# DJ will recommend: comforting, soothing tracks
```

### Preference Evolution

Preferences evolve as the DJ learns:

```python
dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Week 1: Basic preferences
dj.update_preferences("user_001", ["jazz"])
print(dj.user_profiles["user_001"].music_preferences)
# ['jazz']

# Week 2: User explores electronic
dj.update_preferences("user_001", ["electronic", "house"])
print(dj.user_profiles["user_001"].music_preferences)
# ['jazz', 'electronic', 'house']

# Week 3: Discovers sub-genres
dj.update_preferences("user_001", ["deep house", "jazz fusion", "ambient"])
print(dj.user_profiles["user_001"].music_preferences)
# ['jazz', 'electronic', 'house', 'deep house', 'jazz fusion', 'ambient']

# Preferences automatically deduplicated
dj.update_preferences("user_001", ["jazz"])  # Already exists
print(dj.user_profiles["user_001"].music_preferences)
# Still: ['jazz', 'electronic', 'house', 'deep house', 'jazz fusion', 'ambient']
```

### Recommendation Quality

The DJ improves recommendations over time:

**Early Stage** (< 10 interactions):
- Generic recommendations
- Exploring user taste
- Learning patterns

**Growing Stage** (10-50 interactions):
- Personalized recommendations
- Understanding preferences
- Building confidence

**Mature Stage** (50+ interactions):
- Highly personalized recommendations
- Deep understanding
- Predictive suggestions

## Community Connections

Connect with other music lovers to discover new music and build trust.

### Adding Community Connections

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Connect users with similar taste
dj.add_to_community("user_001", "friend_002")
dj.add_to_community("user_001", "friend_003")
dj.add_to_community("user_001", "friend_004")

# Check connections
profile = dj.user_profiles["user_001"]
print(f"Community size: {len(profile.community_connections)}")
# Community size: 3
```

### Community-Aware Interactions

The DJ considers community in responses:

```python
# User asks about community
response = dj.interact("user_001", "What's my music community like?")
print(response)
# "You're part of a trusted community of 3 music lovers. 
#  Together we're discovering amazing sounds!"

# DJ can recommend based on community preferences:
# "Your friend Sarah has been loving this new jazz album, want to check it out?"
# "3 people in your community rated this track 5 stars!"
```

### Community Trust Network

Community connections contribute to overall trust:

```python
def calculate_community_trust(user_id, dj):
    """Calculate trust score including community influence"""
    
    # User's direct trust
    user_trust = dj.get_trust_score(user_id)
    
    # Community trust (average of connected users)
    profile = dj.user_profiles[user_id]
    community_trusts = [
        dj.get_trust_score(friend_id)
        for friend_id in profile.community_connections
        if friend_id in dj.user_profiles
    ]
    
    if community_trusts:
        community_avg = sum(community_trusts) / len(community_trusts)
        # Weighted: 70% user, 30% community
        total_trust = (user_trust * 0.7) + (community_avg * 0.3)
    else:
        total_trust = user_trust
    
    return total_trust

# Example
trust = calculate_community_trust("user_001", dj)
print(f"Total trust (including community): {trust:.2f}")
```

### Privacy in Community

Community features respect privacy:

- ✅ **Opt-in**: Users choose to connect
- ✅ **Transparent**: Users see their connections
- ✅ **Controlled**: Users can disconnect anytime
- ❌ **No tracking**: No hidden data collection
- ❌ **No selling**: Data never sold or shared
- ❌ **No surveillance**: No monitoring without consent

## Usage Examples

### Complete Interaction Example

```python
from qfzz.dj import PersonalizedDJ

# Initialize DJ
dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# First interaction
greeting = dj.greet_user("user_001", "Alex")
print(greeting)
# "Hey Alex! Welcome to QFZZ! I'm DJ Quantum, your personal DJ. 
#  Let's discover some great music together!"

# Share preferences
dj.update_preferences("user_001", ["jazz", "electronic", "ambient"])

# Chat with DJ
response1 = dj.interact("user_001", "I'm feeling really energetic today!")
print(response1)
# "I love that energy! Let me bring up the tempo with some uplifting beats!"

# Request recommendation
response2 = dj.interact("user_001", "Can you recommend something?")
print(response2)
# "Based on your taste for jazz, electronic, ambient, 
#  I've got the perfect track queued up! Let me play something special for you."

# Check trust
trust = dj.get_trust_score("user_001")
print(f"Trust score: {trust:.2f}")
# Trust score: 0.52 (started at 0.5, +0.01 per interaction)

# Add friends
dj.add_to_community("user_001", "friend_002")

# Ask about community
response3 = dj.interact("user_001", "Tell me about my community")
print(response3)
# "You're part of a trusted community of 1 music lovers. 
#  Together we're discovering amazing sounds!"
```

### Multi-User Example

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Multiple users, separate profiles
users = [
    ("user_001", "Alex", ["jazz", "electronic"]),
    ("user_002", "Sam", ["rock", "indie"]),
    ("user_003", "Jordan", ["classical", "ambient"])
]

for user_id, name, preferences in users:
    # Greet each user
    greeting = dj.greet_user(user_id, name)
    print(f"{name}: {greeting}")
    
    # Set preferences
    dj.update_preferences(user_id, preferences)
    
    # Interact
    response = dj.interact(user_id, "Play something for me")
    print(f"{name}: {response}\n")

# Each user has separate profile and context
print(f"Total users: {len(dj.user_profiles)}")
# Total users: 3
```

### Building Trust Over Time

```python
from qfzz.dj import PersonalizedDJ

dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Simulate relationship development
dj.greet_user("user_001", "Alex")

# Week 1: 10 interactions
for i in range(10):
    dj.interact("user_001", f"Message {i}")

trust_week1 = dj.get_trust_score("user_001")
print(f"After 1 week (10 interactions): {trust_week1:.2f}")
# After 1 week (10 interactions): 0.60

# Week 2: 20 more interactions
for i in range(20):
    dj.interact("user_001", f"Message {i}")

trust_week2 = dj.get_trust_score("user_001")
print(f"After 2 weeks (30 interactions): {trust_week2:.2f}")
# After 2 weeks (30 interactions): 0.80

# Week 4: 50 more interactions
for i in range(50):
    dj.interact("user_001", f"Message {i}")

trust_week4 = dj.get_trust_score("user_001")
print(f"After 4 weeks (80 interactions): {trust_week4:.2f}")
# After 4 weeks (80 interactions): 1.00 (capped at 1.0)
```

### Edge Device Integration

```python
from qfzz import QFZZStation
from qfzz.core import StationConfig
from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer

# Configure for edge device
edge_config = EdgeDeviceConfig(
    device_id="smartphone_001",
    device_type="smartphone",
    max_memory_mb=1024,
    max_model_size_mb=100,
    enable_6g=True
)

# Initialize station with edge mode
station_config = StationConfig(
    station_name="My QFZZ",
    edge_mode=True,  # DJ runs on device
    enable_personalization=True
)

station = QFZZStation(config=station_config)
station.start()

# Get DJ (runs locally)
dj = station.get_dj()

# All interactions happen on-device (private)
greeting = dj.greet_user("user_001", "Alex")
response = dj.interact("user_001", "Recommend something chill")

# User data never leaves device
```

## Best Practices

### 1. Regular Interactions

Build trust through consistent interaction:

```python
# ✅ Good: Regular interactions
for day in range(30):  # 30 days
    response = dj.interact("user_001", daily_message())
    # Trust builds steadily

# ❌ Avoid: Sporadic interactions
# Day 1: 100 interactions
# Day 2-30: No interactions
# Trust builds but relationship feels artificial
```

### 2. Clear Preference Updates

Update preferences explicitly:

```python
# ✅ Good: Clear, specific preferences
dj.update_preferences("user_001", [
    "jazz fusion",
    "deep house",
    "ambient electronic",
    "downtempo"
])

# ❌ Avoid: Vague or generic preferences
dj.update_preferences("user_001", ["music", "good songs", "stuff"])
```

### 3. Contextual Conversations

Provide context in your messages:

```python
# ✅ Good: Contextual messages
dj.interact("user_001", "I'm working out, need high-energy music")
dj.interact("user_001", "Winding down after work, something relaxing")
dj.interact("user_001", "Cooking dinner, upbeat but not too intense")

# ❌ Avoid: Context-free requests
dj.interact("user_001", "Music")
dj.interact("user_001", "Play")
dj.interact("user_001", "Next")
```

### 4. Build Community Thoughtfully

Connect with users who share your taste:

```python
# ✅ Good: Meaningful connections
# Only connect with users who have similar preferences
if user_has_similar_taste("user_001", "friend_002"):
    dj.add_to_community("user_001", "friend_002")

# ❌ Avoid: Random connections
# Don't just connect everyone
# Quality > quantity in community
```

### 5. Respect Privacy

Keep user data private:

```python
# ✅ Good: Local processing
dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)
# All data stays on device

# ✅ Good: Opt-in sharing
if user_consents_to_sharing():
    share_with_community(user_profile)

# ❌ Avoid: Automatic data sharing
# Never share without explicit consent
```

### 6. Monitor Trust Development

Track trust score to understand relationship:

```python
# ✅ Good: Monitor and respond to trust levels
trust = dj.get_trust_score("user_001")

if trust < 0.5:
    # Early relationship - be gentle
    approach = "exploratory"
elif trust < 0.7:
    # Growing relationship - be engaging
    approach = "personalized"
else:
    # Strong relationship - be confident
    approach = "highly_personalized"

# Adapt behavior based on trust level
```

### 7. Provide Feedback Mechanisms

Allow users to guide learning:

```python
# ✅ Good: Accept feedback
response = dj.interact("user_001", "That track was perfect!")
# DJ learns this recommendation style works

response = dj.interact("user_001", "Not really feeling this one")
# DJ learns to adjust recommendations

# Implement feedback tracking:
def handle_feedback(user_id, track_id, feedback):
    if feedback == "positive":
        # Reinforce this recommendation style
        strengthen_preference(user_id, track_id)
    elif feedback == "negative":
        # Adjust away from this style
        weaken_preference(user_id, track_id)
```

### 8. Handle Edge Device Constraints

Optimize for device limitations:

```python
from qfzz.edge import EdgeOptimizer, EdgeDeviceConfig

# ✅ Good: Configure for device
config = EdgeDeviceConfig(
    device_id="device_001",
    device_type="smartphone",
    max_memory_mb=1024,
    max_model_size_mb=100
)

optimizer = EdgeOptimizer(config)

# Check optimization needs
model_size = 200.0
recommendations = optimizer.optimize_model(model_size)

if recommendations['optimizations']:
    # Apply optimizations before deploying
    apply_optimizations(recommendations['optimizations'])

# ❌ Avoid: Ignoring device constraints
# Don't deploy 500 MB model to 256 MB device
```

### 9. Maintain Conversation Quality

Keep conversations natural and engaging:

```python
# ✅ Good: Natural conversation flow
conversation = [
    ("user", "I'm in a great mood today!"),
    ("dj", "I love that energy! What kind of music fits your vibe?"),
    ("user", "Something uplifting, maybe electronic?"),
    ("dj", "Perfect! Let me queue up some energetic electronic tracks...")
]

# ❌ Avoid: Robotic interactions
# User: "Music"
# DJ: "Playing music"
# User: "Next"
# DJ: "Next track"
```

### 10. Document User Journey

Track the relationship development:

```python
# ✅ Good: Track milestones
def track_milestones(user_id, dj):
    profile = dj.user_profiles[user_id]
    interactions = len(profile.interaction_history)
    trust = dj.get_trust_score(user_id)
    
    milestones = {
        10: "First 10 conversations",
        50: "50 sessions together",
        100: "100 sessions milestone",
        500: "Long-time listener"
    }
    
    if interactions in milestones:
        celebrate_milestone(user_id, milestones[interactions])

# Celebrate growth in the relationship
```

## Integration with QFZZ Station

Complete integration example:

```python
from qfzz import QFZZStation
from qfzz.core import StationConfig

# Initialize station with personalization
config = StationConfig(
    station_name="My Personal QFZZ",
    edge_mode=True,
    enable_personalization=True,  # Enable DJ
    blockchain_enabled=True        # Trust network
)

station = QFZZStation(config=config)
station.start()

# Get the DJ (automatically initialized)
dj = station.get_dj()

# Start your personalized music journey
greeting = dj.greet_user("your_user_id", "Your Name")
print(greeting)

# Update your preferences
dj.update_preferences("your_user_id", ["your", "favorite", "genres"])

# Start chatting
response = dj.interact("your_user_id", "What should I listen to today?")
print(response)
```

## Advanced Features

### Custom DJ Names

Personalize your DJ:

```python
# Create DJ with custom name
dj = PersonalizedDJ(name="DJ Nova", edge_mode=True)

greeting = dj.greet_user("user_001", "Alex")
# "Hey Alex! Welcome to QFZZ! I'm DJ Nova, your personal DJ..."
```

### Multiple DJs

Have multiple DJs for different contexts:

```python
# Work DJ - focus and productivity
work_dj = PersonalizedDJ(name="DJ Focus", edge_mode=True)

# Workout DJ - energy and motivation  
workout_dj = PersonalizedDJ(name="DJ Energy", edge_mode=True)

# Relaxation DJ - calm and peaceful
relax_dj = PersonalizedDJ(name="DJ Zen", edge_mode=True)

# Use appropriate DJ for context
if context == "working":
    response = work_dj.interact(user_id, message)
elif context == "workout":
    response = workout_dj.interact(user_id, message)
else:
    response = relax_dj.interact(user_id, message)
```

## Next Steps

- **[Edge Deployment Guide](edge-deployment.md)** - Deploy DJ on edge devices
- **[API Reference](../api/dj.md)** - Detailed DJ API documentation
- **[Architecture](../architecture.md)** - Understand system design
- **Examples** - See `examples/personalized_dj_demo.py` in the repository

## Support

For issues and questions:
- Review [best practices](#best-practices) above
- Check [usage examples](#usage-examples)
- See the examples directory in the repository
- Open an issue on GitHub
- Consult [API documentation](../api/dj.md)
