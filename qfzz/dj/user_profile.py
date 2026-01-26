"""User Profile Management"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserProfile:
    """User profile for personalization

    Attributes:
        user_id: Unique user identifier
        name: User's display name
        music_preferences: List of music genres/styles user likes
        interaction_history: History of interactions with the DJ
        trust_score: User's trust score in the community (0.0-1.0)
        community_connections: List of connected user IDs
        created_at: Profile creation timestamp
    """

    user_id: str
    name: str
    music_preferences: list[str] = field(default_factory=list)
    interaction_history: list[dict[str, Any]] = field(default_factory=list)
    trust_score: float = 0.5
    community_connections: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
