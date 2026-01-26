"""
Personalized DJ with user profiling and recommendations.
"""

import logging
import random
from datetime import datetime
from typing import Any

from qfzz.blockchain import SovereignLedger
from qfzz.knowledge import QFZZKnowledgeGraph
from qfzz.library import ContentScanner
from qfzz.library.fetcher import ContentFetcher
from qfzz.llm.router import LLMRouter

from .ai_dj import AIDJ
from .profiles import UserProfile

logger = logging.getLogger(__name__)


class PersonalizedDJ:
    """
    AI-powered personalized DJ that learns user preferences and creates
    tailored playlists with trust-based content filtering.
    """

    def __init__(
        self,
        llm_model: str = "llama3",
        api_key: str | None = None,
        dj_persona: str = "energetic",
        enable_ai_dj: bool = True,
    ):
        """
        Initialize the Personalized DJ.

        Args:
            llm_model: Name of the LLM model to use (default: llama3) - deprecated
            api_key: Optional API key for cloud providers - deprecated
            dj_persona: DJ persona for AI commentary (energetic, chill, intellectual, storyteller)
            enable_ai_dj: Whether to enable AI DJ commentary
        """
        self._user_profiles: dict[str, UserProfile] = {}
        self._content_catalog: list[dict[str, Any]] = []
        self._genre_similarity: dict[str, list[str]] = self._init_genre_similarity()
        self.kg = QFZZKnowledgeGraph()  # Initialize Knowledge Graph
        self.scanner = ContentScanner(library_path="./qfzz_audio_content")  # Initialize Scanner
        self.ledger = SovereignLedger()  # Initialize Blockchain Ledger
        self.fetcher = ContentFetcher(download_dir="./qfzz_audio_content")  # Initialize Fetcher

        # Initialize LLM Router with automatic provider selection and fallback
        self.llm_router = LLMRouter()

        # Initialize AI DJ if enabled
        self.ai_dj = None
        if enable_ai_dj:
            try:
                self.ai_dj = AIDJ(persona=dj_persona)
                logger.info(
                    f"AI DJ initialized with persona: {dj_persona} ({self.ai_dj.get_persona_name()})"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize AI DJ: {e}")
                self.ai_dj = None

        # Log available providers
        available = self.llm_router.get_available_providers()
        logger.info(
            f"Personalized DJ initialized with {len(available)} available LLM providers: {', '.join(available)}"
        )

        if llm_model != "llama3" or api_key:
            logger.warning(
                "llm_model and api_key parameters are deprecated. Use environment variables instead."
            )

    def request_track(self, url: str) -> dict[str, Any] | None:
        """Download and register a track from a URL."""
        track = self.fetcher.fetch_from_url(url)
        if track:
            # Scan it for deep features immediately?
            # For now, just trust fetcher metadata
            self.kg.add_track_node(track["filename"], track)
            if self.ledger:
                self.ledger.record_event(
                    "TRACK_INGESTED", {"url": url, "filename": track["filename"]}
                )
            return track
        return None

    def interact(self, user_id: str, message: str) -> str:
        """
        Chat with the DJ.

        Args:
            user_id: User identifier
            message: User message

        Returns:
            DJ response
        """
        # Use AI DJ if available, otherwise use LLM router directly
        if self.ai_dj:
            return self.ai_dj.respond_to_listener(message)

        # Fallback to original implementation
        profile = self.get_or_create_profile(user_id)

        # Construct system prompt with user context
        context = f"""You are a personalized AI Radio DJ named QFZZ.
        User: {user_id}
        Preferences: {profile.genres if hasattr(profile, "genres") else "Unknown"}

        Keep it brief (under 50 words), cool, and radio-friendly."""

        # Get response from LLM router
        result = self.llm_router.generate(message, system_prompt=context, max_tokens=200)
        return result["text"]

    def generate_segue(
        self, track_prev: dict[str, Any] | None, track_next: dict[str, Any]
    ) -> str:
        """
        Generate a radio segue connecting two tracks using Knowledge Graph context.
        """
        # Use AI DJ if available for better commentary
        if self.ai_dj:
            if not track_prev:
                return self.ai_dj.introduce_track(track_next)
            else:
                return self.ai_dj.generate_transition(track_prev, track_next)

        # Fallback to original implementation
        if not track_prev:
            prompt = (
                f"Introduce the first track: '{track_next['title']}' by {track_next['artist']}."
            )
        else:
            # Detect relationships via Knowledge Graph logic (simple heuristic for now)
            # In a real scenario, we'd query self.kg.graph.get_shortest_path(prev, next)

            rels = []
            if track_prev.get("artist") == track_next.get("artist"):
                rels.append("same artist")
            if track_prev.get("genre") == track_next.get("genre"):
                rels.append("same vibe")

            # Check deep features if available
            fp_prev = track_prev.get("fingerprint")
            fp_next = track_next.get("fingerprint")

            if fp_prev and fp_next:
                if fp_prev.get("key") == fp_next.get("key"):
                    rels.append(f"staying in the key of {fp_prev['key']}")

                bpm_diff = fp_next["bpm"] - fp_prev["bpm"]
                if bpm_diff > 10:
                    rels.append("bumping up the energy")
                elif bpm_diff < -10:
                    rels.append("slowing things down")

            connection = ", ".join(rels) if rels else "switching gears"

            prompt = (
                f"You are QFZZ, a hyper-intelligent quantum radio host. \n"
                f"We just heard '{track_prev['title']}' by {track_prev['artist']}. \n"
                f"Now playing '{track_next['title']}' by {track_next['artist']}. \n"
                f"Connection: {connection}. \n"
                f"Write a 1-sentence segue. Be cool, futuristic, and mention the connection if interesting."
            )

        # Record this AI Generation to the Sovereign Ledger
        if hasattr(self, "ledger"):
            self.ledger.record_event(
                "SEGUE_GENERATION",
                {
                    "prev_track": track_prev.get("title") if track_prev else "None",
                    "next_track": track_next.get("title"),
                    "prompt_hash": hash(prompt),
                },
            )

        # Generate segue using LLM router
        result = self.llm_router.generate(
            prompt, system_prompt="You are QFZZ, the Pulse of the Quantum Realm.", max_tokens=100
        )
        return result["text"]

    def _init_genre_similarity(self) -> dict[str, list[str]]:
        """
        Initialize genre similarity mappings.

        Returns:
            Dictionary mapping genres to similar genres
        """
        return {
            "rock": ["alternative", "indie", "punk", "metal"],
            "pop": ["dance", "electronic", "indie-pop", "synth-pop"],
            "jazz": ["blues", "soul", "funk", "swing"],
            "classical": ["orchestral", "baroque", "romantic", "contemporary"],
            "hip-hop": ["rap", "trap", "r&b", "urban"],
            "electronic": ["techno", "house", "trance", "ambient"],
            "folk": ["acoustic", "country", "americana", "singer-songwriter"],
            "metal": ["hard-rock", "progressive", "death-metal", "black-metal"],
        }

    def get_or_create_profile(
        self, user_id: str, initial_preferences: dict[str, Any] | None = None
    ) -> UserProfile:
        """
        Get existing user profile or create a new one.

        Args:
            user_id: Unique user identifier
            initial_preferences: Optional initial preferences

        Returns:
            UserProfile instance
        """
        if user_id not in self._user_profiles:
            profile = UserProfile(user_id=user_id)

            # Apply initial preferences if provided
            if initial_preferences:
                if "genres" in initial_preferences:
                    for genre, weight in initial_preferences["genres"].items():
                        profile.update_genre_preference(genre, weight)

                if "artists" in initial_preferences:
                    for artist, weight in initial_preferences["artists"].items():
                        profile.update_artist_preference(artist, weight)

                if "energy_level" in initial_preferences:
                    profile.energy_level = initial_preferences["energy_level"]

                if "discovery_factor" in initial_preferences:
                    profile.discovery_factor = initial_preferences["discovery_factor"]

            self._user_profiles[user_id] = profile
            logger.info(f"Created new profile for user: {user_id}")

        return self._user_profiles[user_id]

    def recommend(
        self, user_id: str, preferences: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Generate personalized recommendations for a user.

        Args:
            user_id: User identifier
            preferences: Optional real-time preferences to override profile

        Returns:
            List of recommended tracks
        """
        profile = self.get_or_create_profile(user_id, preferences)

        # Get content pool
        candidates = self._get_candidate_tracks(profile)

        # Score and rank candidates
        scored_tracks = []
        for track in candidates:
            score = self._calculate_track_score(track, profile, preferences)
            scored_tracks.append((score, track))

        # Sort by score (descending)
        scored_tracks.sort(key=lambda x: x[0], reverse=True)

        # Apply discovery factor for exploration
        recommendations = self._apply_discovery(scored_tracks, profile.discovery_factor)

        logger.info(f"Generated {len(recommendations)} recommendations for {user_id}")
        return recommendations

    def _get_candidate_tracks(self, profile: UserProfile) -> list[dict[str, Any]]:
        """
        Get candidate tracks based on user profile.

        Args:
            profile: User profile

        Returns:
            List of candidate tracks
        """
        # If we have a catalog, use it
        if self._content_catalog:
            return self._content_catalog

        # Otherwise generate sample tracks for demonstration
        return self._generate_sample_tracks(profile)

    def _generate_sample_tracks(self, profile: UserProfile) -> list[dict[str, Any]]:
        """
        Generate sample tracks for demonstration.

        Args:
            profile: User profile

        Returns:
            List of sample tracks
        """
        genres = list(profile.genres.keys()) if profile.genres else ["rock", "pop", "jazz"]

        tracks = []
        for i in range(50):
            genre = random.choice(genres)
            track = {
                "track_id": f"track_{i:04d}",
                "title": f"Track {i}",
                "artist": f"Artist {i % 10}",
                "album": f"Album {i % 5}",
                "genre": genre,
                "mood": random.choice(["upbeat", "mellow", "energetic", "calm"]),
                "energy": random.uniform(0.0, 1.0),
                "tempo": random.choice(["slow", "medium", "fast"]),
                "duration": random.randint(180, 300),
                "content_id": f"content_{i:04d}",
                "creator_id": f"creator_{i % 10}",
            }
            tracks.append(track)

        return tracks

    def _calculate_track_score(
        self,
        track: dict[str, Any],
        profile: UserProfile,
        preferences: dict[str, Any] | None = None,
    ) -> float:
        """
        Calculate compatibility score for a track.

        Args:
            track: Track dictionary
            profile: User profile
            preferences: Optional real-time preferences

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        weights_sum = 0.0

        # Genre matching (weight: 0.3)
        genre_weight = 0.3
        if track.get("genre") in profile.genres:
            score += profile.genres[track["genre"]] * genre_weight
        elif track.get("genre") in self._get_similar_genres(profile.genres.keys()):
            score += 0.5 * genre_weight
        weights_sum += genre_weight

        # Artist matching (weight: 0.25)
        artist_weight = 0.25
        if track.get("artist") in profile.artists:
            score += profile.artists[track["artist"]] * artist_weight
        weights_sum += artist_weight

        # Energy level matching (weight: 0.2)
        energy_weight = 0.2
        if "energy" in track:
            energy_diff = abs(track["energy"] - profile.energy_level)
            energy_score = 1.0 - energy_diff
            score += energy_score * energy_weight
        weights_sum += energy_weight

        # Tempo matching (weight: 0.15)
        tempo_weight = 0.15
        if track.get("tempo") == profile.tempo_preference or profile.tempo_preference == "varied":
            score += tempo_weight
        weights_sum += tempo_weight

        # Mood matching (weight: 0.1)
        mood_weight = 0.1
        if track.get("mood") in profile.moods:
            score += profile.moods[track["mood"]] * mood_weight
        weights_sum += mood_weight

        # Normalize score
        if weights_sum > 0:
            score = score / weights_sum

        return min(1.0, max(0.0, score))

    def _get_similar_genres(self, genres: list[str]) -> list[str]:
        """
        Get similar genres based on genre similarity mappings.

        Args:
            genres: List of genre names

        Returns:
            List of similar genres
        """
        similar = []
        for genre in genres:
            if genre in self._genre_similarity:
                similar.extend(self._genre_similarity[genre])
        return list(set(similar))

    def _apply_discovery(
        self, scored_tracks: list[tuple], discovery_factor: float
    ) -> list[dict[str, Any]]:
        """
        Apply discovery factor to introduce serendipity.

        Args:
            scored_tracks: List of (score, track) tuples
            discovery_factor: Discovery factor (0.0-1.0)

        Returns:
            List of tracks with discovery applied
        """
        if not scored_tracks:
            return []

        # Split into high-scoring and discovery candidates
        split_point = max(1, int(len(scored_tracks) * (1.0 - discovery_factor)))

        high_scores = scored_tracks[:split_point]
        discovery_pool = scored_tracks[split_point:]

        # Take high-scoring tracks
        recommendations = [track for _, track in high_scores]

        # Add random discovery tracks
        if discovery_pool:
            num_discovery = int(
                len(recommendations) * discovery_factor / (1.0 - discovery_factor + 0.01)
            )
            num_discovery = min(num_discovery, len(discovery_pool))

            discovery_tracks = random.sample(discovery_pool, num_discovery)
            recommendations.extend([track for _, track in discovery_tracks])

        return recommendations

    def record_feedback(
        self, user_id: str, track_id: str, interaction_type: str, rating: float | None = None
    ) -> None:
        """
        Record user feedback to improve recommendations.

        Args:
            user_id: User identifier
            track_id: Track identifier
            interaction_type: Type of interaction (play, skip, like, dislike, etc.)
            rating: Optional explicit rating
        """
        profile = self.get_or_create_profile(user_id)

        # Record interaction
        interaction = {
            "track_id": track_id,
            "type": interaction_type,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
        }
        profile.add_interaction(interaction)

        # Update profile based on feedback
        self._update_profile_from_feedback(profile, track_id, interaction_type, rating)

        logger.debug(f"Recorded feedback for user {user_id}: {interaction_type} on {track_id}")

    def _update_profile_from_feedback(
        self, profile: UserProfile, track_id: str, interaction_type: str, rating: float | None
    ) -> None:
        """
        Update user profile based on feedback.

        Args:
            profile: User profile to update
            track_id: Track identifier
            interaction_type: Type of interaction
            rating: Optional rating
        """
        # Find track in catalog
        track = None
        for t in self._content_catalog:
            if t.get("track_id") == track_id:
                track = t
                break

        if not track:
            return

        # Calculate feedback strength
        strength = 0.0
        if interaction_type == "like":
            strength = 0.1
        elif interaction_type == "dislike":
            strength = -0.1
        elif interaction_type == "skip":
            strength = -0.05
        elif interaction_type == "play":
            strength = 0.05
        elif interaction_type == "favorite":
            strength = 0.2

        if rating is not None:
            strength = (rating - 0.5) * 0.2

        # Update genre preferences
        if "genre" in track:
            genre = track["genre"]
            current_weight = profile.genres.get(genre, 0.5)
            new_weight = max(0.0, min(1.0, current_weight + strength))
            profile.update_genre_preference(genre, new_weight)

        # Update artist preferences
        if "artist" in track:
            artist = track["artist"]
            current_weight = profile.artists.get(artist, 0.5)
            new_weight = max(0.0, min(1.0, current_weight + strength))
            profile.update_artist_preference(artist, new_weight)

        # Update mood preferences
        if "mood" in track:
            mood = track["mood"]
            current_weight = profile.moods.get(mood, 0.5)
            new_weight = max(0.0, min(1.0, current_weight + strength))
            profile.update_mood_preference(mood, new_weight)

    def add_content(self, tracks: list[dict[str, Any]]) -> None:
        """
        Add tracks to content catalog.

        Args:
            tracks: List of track dictionaries
        """
        self._content_catalog.extend(tracks)
        logger.info(f"Added {len(tracks)} tracks to catalog. Total: {len(self._content_catalog)}")

    def get_profile(self, user_id: str) -> UserProfile | None:
        """
        Get user profile.

        Args:
            user_id: User identifier

        Returns:
            UserProfile if exists, None otherwise
        """
        return self._user_profiles.get(user_id)

    def get_ai_dj_persona(self) -> str | None:
        """
        Get current AI DJ persona name.

        Returns:
            Persona name if AI DJ is enabled, None otherwise
        """
        if self.ai_dj:
            return self.ai_dj.get_persona_name()
        return None

    def set_ai_dj_persona(self, persona: str) -> bool:
        """
        Change AI DJ persona.

        Args:
            persona: New persona name (energetic, chill, intellectual, storyteller)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.ai_dj = AIDJ(persona=persona)
            logger.info(f"AI DJ persona changed to: {persona}")
            return True
        except Exception as e:
            logger.error(f"Failed to change AI DJ persona: {e}")
            return False

    def generate_station_id(self) -> str:
        """
        Generate station identification.

        Returns:
            Station ID text
        """
        if self.ai_dj:
            return self.ai_dj.generate_station_id()

        # Fallback
        return "You're listening to QFZZ FuzzyRadio!"
