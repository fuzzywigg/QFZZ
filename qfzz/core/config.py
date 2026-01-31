"""
Configuration management for QFZZ Station.
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StationConfig:
    """
    Configuration for a QFZZ Radio Station.

    Attributes:
        station_id: Unique identifier for the station
        station_name: Human-readable station name
        max_playlist_size: Maximum number of tracks in playlist
        trust_threshold: Minimum trust score for content (0.0-1.0)
        enable_blockchain: Enable blockchain trust network
        enable_edge_optimization: Enable edge device optimization
        streaming_quality: Default streaming quality
        allowed_licenses: List of acceptable content licenses
        cache_size_mb: Cache size in megabytes
        metadata: Additional configuration metadata
    """

    station_id: str
    station_name: str
    max_playlist_size: int = 100
    trust_threshold: float = 0.6
    enable_blockchain: bool = True
    enable_edge_optimization: bool = True
    streaming_quality: str = "high"
    allowed_licenses: list[str] = field(default_factory=lambda: ["CC-BY", "CC-BY-SA", "CC0"])
    cache_size_mb: int = 500
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        if not self.station_id or not isinstance(self.station_id, str):
            raise ValueError("station_id must be a non-empty string")

        if not self.station_name or not isinstance(self.station_name, str):
            raise ValueError("station_name must be a non-empty string")

        if self.max_playlist_size < 1:
            raise ValueError("max_playlist_size must be positive")

        if not 0.0 <= self.trust_threshold <= 1.0:
            raise ValueError("trust_threshold must be between 0.0 and 1.0")

        if self.streaming_quality not in ["low", "medium", "high", "lossless"]:
            raise ValueError("streaming_quality must be one of: low, medium, high, lossless")

        if self.cache_size_mb < 0:
            raise ValueError("cache_size_mb must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "station_id": self.station_id,
            "station_name": self.station_name,
            "max_playlist_size": self.max_playlist_size,
            "trust_threshold": self.trust_threshold,
            "enable_blockchain": self.enable_blockchain,
            "enable_edge_optimization": self.enable_edge_optimization,
            "streaming_quality": self.streaming_quality,
            "allowed_licenses": self.allowed_licenses,
            "cache_size_mb": self.cache_size_mb,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StationConfig":
        """Create configuration from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "StationConfig":
        """Create configuration from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
