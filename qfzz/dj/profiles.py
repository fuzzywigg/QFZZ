"""
User profile management for personalized recommendations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserProfile:
    """
    User profile for personalized DJ recommendations.

    Attributes:
        user_id: Unique user identifier
        genres: Preferred music genres with weights
        artists: Preferred artists with weights
        moods: Preferred moods with weights
        energy_level: Preferred energy level (0.0-1.0)
        tempo_preference: Preferred tempo range (slow, medium, fast)
        discovery_factor: Willingness to discover new music (0.0-1.0)
        interaction_history: History of user interactions
        created_at: Profile creation timestamp
        updated_at: Profile last update timestamp
    """

    user_id: str
    genres: dict[str, float] = field(default_factory=dict)
    artists: dict[str, float] = field(default_factory=dict)
    moods: dict[str, float] = field(default_factory=dict)
    energy_level: float = 0.5
    tempo_preference: str = "medium"
    discovery_factor: float = 0.3
    interaction_history: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate profile after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate profile parameters.

        Raises:
            ValueError: If any parameter is invalid
        """
        if not self.user_id:
            raise ValueError("user_id must be non-empty")

        if not 0.0 <= self.energy_level <= 1.0:
            raise ValueError("energy_level must be between 0.0 and 1.0")

        if self.tempo_preference not in ["slow", "medium", "fast", "varied"]:
            raise ValueError("tempo_preference must be one of: slow, medium, fast, varied")

        if not 0.0 <= self.discovery_factor <= 1.0:
            raise ValueError("discovery_factor must be between 0.0 and 1.0")

    def update_genre_preference(self, genre: str, weight: float) -> None:
        """
        Update genre preference weight.

        Args:
            genre: Genre name
            weight: Preference weight (0.0-1.0)
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")

        self.genres[genre] = weight
        self.updated_at = datetime.now().isoformat()

    def update_artist_preference(self, artist: str, weight: float) -> None:
        """
        Update artist preference weight.

        Args:
            artist: Artist name
            weight: Preference weight (0.0-1.0)
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")

        self.artists[artist] = weight
        self.updated_at = datetime.now().isoformat()

    def update_mood_preference(self, mood: str, weight: float) -> None:
        """
        Update mood preference weight.

        Args:
            mood: Mood name
            weight: Preference weight (0.0-1.0)
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")

        self.moods[mood] = weight
        self.updated_at = datetime.now().isoformat()

    def add_interaction(self, interaction: dict[str, Any]) -> None:
        """
        Add interaction to history.

        Args:
            interaction: Interaction details dictionary
        """
        interaction["timestamp"] = datetime.now().isoformat()
        self.interaction_history.append(interaction)
        self.updated_at = datetime.now().isoformat()

        # Keep only last 1000 interactions
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-1000:]

    def get_top_genres(self, limit: int = 5) -> list[str]:
        """
        Get top preferred genres.

        Args:
            limit: Maximum number of genres to return

        Returns:
            List of genre names sorted by preference
        """
        sorted_genres = sorted(self.genres.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, _ in sorted_genres[:limit]]

    def get_top_artists(self, limit: int = 10) -> list[str]:
        """
        Get top preferred artists.

        Args:
            limit: Maximum number of artists to return

        Returns:
            List of artist names sorted by preference
        """
        sorted_artists = sorted(self.artists.items(), key=lambda x: x[1], reverse=True)
        return [artist for artist, _ in sorted_artists[:limit]]

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "user_id": self.user_id,
            "genres": self.genres,
            "artists": self.artists,
            "moods": self.moods,
            "energy_level": self.energy_level,
            "tempo_preference": self.tempo_preference,
            "discovery_factor": self.discovery_factor,
            "interaction_history": self.interaction_history,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
