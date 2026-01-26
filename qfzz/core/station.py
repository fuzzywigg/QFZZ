"""
Main QFZZ Station orchestrator.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from .config import StationConfig

logger = logging.getLogger(__name__)


class QFZZStation:
    """
    Main orchestrator for a QFZZ Radio Station.

    Coordinates personalized DJ, dataset management, blockchain trust,
    edge optimization, and streaming capabilities.
    """

    def __init__(self, config: StationConfig):
        """
        Initialize QFZZ Station.

        Args:
            config: Station configuration
        """
        self.config = config
        self._running = False
        self._current_playlist: list[dict[str, Any]] = []
        self._listeners: dict[str, Any] = {}

        # Components will be initialized lazily
        self._dj = None
        self._dataset_manager = None
        self._trust_network = None
        self._edge_optimizer = None
        self._player = None

        logger.info(f"Initialized QFZZ Station: {config.station_name} ({config.station_id})")

    def start(self) -> None:
        """Start the radio station."""
        if self._running:
            logger.warning("Station is already running")
            return

        logger.info(f"Starting station: {self.config.station_name}")
        self._running = True
        self._initialize_components()
        logger.info("Station started successfully")

    def stop(self) -> None:
        """Stop the radio station."""
        if not self._running:
            logger.warning("Station is not running")
            return

        logger.info(f"Stopping station: {self.config.station_name}")
        self._running = False
        self._cleanup_components()
        logger.info("Station stopped successfully")

    def _initialize_components(self) -> None:
        """Initialize station components based on configuration."""
        # Import here to avoid circular dependencies
        from qfzz.datasets.manager import DatasetManager
        from qfzz.dj.personalized_dj import PersonalizedDJ
        from qfzz.streaming.player import MusicPlayer

        self._dj = PersonalizedDJ()
        self._dataset_manager = DatasetManager(allowed_licenses=self.config.allowed_licenses)
        self._player = MusicPlayer()

        if self.config.enable_blockchain:
            from qfzz.blockchain.trust_network import BlockchainTrustNetwork

            self._trust_network = BlockchainTrustNetwork()
            logger.info("Blockchain trust network enabled")

        if self.config.enable_edge_optimization:
            from qfzz.edge.optimizer import EdgeOptimizer

            self._edge_optimizer = EdgeOptimizer()
            logger.info("Edge optimization enabled")

    def _cleanup_components(self) -> None:
        """Cleanup station components."""
        self._dj = None
        self._dataset_manager = None
        self._trust_network = None
        self._edge_optimizer = None
        self._player = None

    def add_listener(self, user_id: str, preferences: Optional[dict[str, Any]] = None) -> None:
        """
        Add a listener to the station.

        Args:
            user_id: Unique user identifier
            preferences: Optional user preferences
        """
        if not self._running:
            raise RuntimeError("Station is not running")

        self._listeners[user_id] = {
            "user_id": user_id,
            "preferences": preferences or {},
            "connected_at": datetime.now().isoformat(),
            "playlist": [],
        }

        logger.info(f"Added listener: {user_id}")

    def remove_listener(self, user_id: str) -> None:
        """
        Remove a listener from the station.

        Args:
            user_id: User identifier to remove
        """
        if user_id in self._listeners:
            del self._listeners[user_id]
            logger.info(f"Removed listener: {user_id}")

    def generate_playlist(self, user_id: str) -> list[dict[str, Any]]:
        """
        Generate personalized playlist for a user.

        Args:
            user_id: User identifier

        Returns:
            List of track dictionaries
        """
        if not self._running:
            raise RuntimeError("Station is not running")

        if user_id not in self._listeners:
            raise ValueError(f"User {user_id} is not a listener")

        user_data = self._listeners[user_id]
        preferences = user_data.get("preferences", {})

        # Get recommendations from DJ
        recommendations = self._dj.recommend(user_id, preferences)

        # Filter by trust threshold if blockchain is enabled
        if self._trust_network:
            recommendations = [
                track
                for track in recommendations
                if self._trust_network.get_trust_score(
                    track.get("content_id", ""), track.get("creator_id", "")
                )
                >= self.config.trust_threshold
            ]

        # Limit playlist size
        playlist = recommendations[: self.config.max_playlist_size]

        # Store playlist for user
        self._listeners[user_id]["playlist"] = playlist

        logger.info(f"Generated playlist for {user_id}: {len(playlist)} tracks")
        return playlist

    def record_interaction(
        self, user_id: str, track_id: str, interaction_type: str, rating: Optional[float] = None
    ) -> None:
        """
        Record user interaction with a track.

        Args:
            user_id: User identifier
            track_id: Track identifier
            interaction_type: Type of interaction (play, skip, like, etc.)
            rating: Optional rating value
        """
        if not self._running:
            raise RuntimeError("Station is not running")

        if user_id not in self._listeners:
            raise ValueError(f"User {user_id} is not a listener")

        # Record with DJ for learning
        self._dj.record_feedback(user_id, track_id, interaction_type, rating)

        logger.debug(f"Recorded {interaction_type} for user {user_id} on track {track_id}")

    def get_station_stats(self) -> dict[str, Any]:
        """
        Get current station statistics.

        Returns:
            Dictionary of station statistics
        """
        return {
            "station_id": self.config.station_id,
            "station_name": self.config.station_name,
            "running": self._running,
            "listener_count": len(self._listeners),
            "blockchain_enabled": self.config.enable_blockchain,
            "edge_optimization_enabled": self.config.enable_edge_optimization,
            "trust_threshold": self.config.trust_threshold,
            "streaming_quality": self.config.streaming_quality,
        }

    def is_running(self) -> bool:
        """Check if station is running."""
        return self._running
