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
from qfzz import PersonalizedDJ

# Create DJ
dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Greet user
greeting = dj.greet_user("user_001", "Alex")
print(greeting)

# Interact
response = dj.interact("user_001", "Can you recommend some music?")
print(response)

# Update preferences
dj.update_preferences("user_001", ["jazz", "electronic"])

# Check trust score
trust_score = dj.get_trust_score("user_001")
print(f"Trust score: {trust_score}")
```
