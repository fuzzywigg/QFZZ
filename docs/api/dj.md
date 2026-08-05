# Personalized DJ API

The DJ module provides AI-powered personalized music curation and interaction.

## PersonalizedDJ

::: qfzz.dj.personalized_dj.PersonalizedDJ
    options:
      show_root_heading: true
      show_source: true

## UserProfile

::: qfzz.dj.user_profile.UserProfile
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from qfzz.dj.personalized_dj import PersonalizedDJ

# Create DJ
dj = PersonalizedDJ(dj_persona="energetic", enable_ai_dj=True)

# Interact
response = dj.interact("user_001", "Can you recommend some music?")
print(response)

# LLM recommendation payload with edge/fallback metadata
recommendation = dj.generate_llm_recommendation_response(
    user_id="user_001",
    message="I want upbeat electronic tracks",
    max_tracks=5,
    include_tts=False,
)
print(recommendation["response"])
print(recommendation["execution_mode"])  # edge-local | cloud | fallback
```

## Backend Endpoints

When `StreamingServer` has a DJ instance attached, these endpoints are available:

- `POST /api/dj/chat` with JSON body `{ "user_id": "...", "message": "...", "include_tts": false }`
- `POST /api/dj/recommendations` with JSON body `{ "user_id": "...", "message": "...", "preferences": {}, "max_tracks": 5, "include_tts": false }`
- `GET /api/llm/providers` for provider health/status
