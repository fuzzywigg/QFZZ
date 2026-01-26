"""
AI-powered DJ with personality and voice synthesis.

Generates contextual commentary for tracks with different personas
and integrates with text-to-speech for audio output.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from qfzz.core.llm_router import LLMRouter
from qfzz.core.state import StateManager
from qfzz.dj.tts_client import TTSClient

logger = logging.getLogger(__name__)


class AIDJ:
    """AI-powered DJ with personality and voice."""

    def __init__(
        self,
        persona: str = "energetic",
        voice_id: str | None = None,
        enable_tts: bool = False,
        tts_provider: str = "openai",
        personas_config_path: str = "config/dj-personas.json",
    ):
        """
        Initialize AI DJ.

        Args:
            persona: DJ personality (energetic, chill, intellectual, storyteller)
            voice_id: Voice ID for TTS (optional, uses persona default if not provided)
            enable_tts: Whether to enable text-to-speech
            tts_provider: TTS provider to use ('openai', 'elevenlabs', 'google')
            personas_config_path: Path to personas configuration file
        """
        self.persona = persona
        self.personas_config = self._load_personas_config(personas_config_path)

        # Load persona configuration
        if persona not in self.personas_config.get("personas", {}):
            logger.warning(f"Unknown persona '{persona}', defaulting to 'energetic'")
            self.persona = "energetic"

        self.persona_config = self.personas_config["personas"][self.persona]

        # Use provided voice_id or default from persona config
        self.voice_id = voice_id or self.persona_config.get("voice_id", "alloy")

        # Initialize LLM router and state manager
        self.llm_router = LLMRouter()
        self.state = StateManager()

        # Initialize TTS client if enabled
        self.tts_client = None
        if enable_tts:
            try:
                self.tts_client = TTSClient(provider=tts_provider)
                if not self.tts_client.is_available():
                    logger.warning("TTS client initialized but not available")
                    self.tts_client = None
            except Exception as e:
                logger.error(f"Failed to initialize TTS client: {e}")
                self.tts_client = None

        logger.info(
            f"AI DJ initialized with persona '{self.persona}' ({self.persona_config['name']})"
        )

    def _load_personas_config(self, config_path: str) -> dict[str, Any]:
        """
        Load personas configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Personas configuration dictionary
        """
        config_file = Path(config_path)

        if not config_file.exists():
            logger.warning(f"Personas config not found at {config_path}, using defaults")
            return self._get_default_personas_config()

        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load personas config: {e}")
            return self._get_default_personas_config()

    def _get_default_personas_config(self) -> dict[str, Any]:
        """Get default personas configuration."""
        return {
            "personas": {
                "energetic": {
                    "name": "Fuzzy Beats",
                    "description": "High-energy DJ who keeps the party going",
                    "voice_id": "alloy",
                    "style": "upbeat, enthusiastic, uses exclamations",
                    "temperature": 0.8,
                    "banned_phrases": [
                        "AI",
                        "language model",
                        "generated",
                        "artificial intelligence",
                    ],
                },
                "chill": {
                    "name": "Smooth Vibes",
                    "description": "Laid-back DJ for relaxation",
                    "voice_id": "nova",
                    "style": "mellow, smooth, contemplative",
                    "temperature": 0.6,
                    "banned_phrases": ["AI", "language model", "artificial intelligence"],
                },
            }
        }

    def _filter_banned_phrases(self, text: str) -> str:
        """
        Filter out banned phrases from generated text.

        Args:
            text: Text to filter

        Returns:
            Filtered text
        """
        banned_phrases = self.persona_config.get("banned_phrases", [])

        # Also get global banned phrases from DJ memory
        try:
            dj_memory = self.state.get_dj_memory()
            banned_phrases.extend(dj_memory.get("banned_phrases", []))
        except Exception as e:
            logger.debug(f"Could not load DJ memory banned phrases: {e}")

        # Remove duplicates
        banned_phrases = list(set(banned_phrases))

        filtered_text = text
        for phrase in banned_phrases:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            filtered_text = pattern.sub("", filtered_text)

        # Clean up extra spaces
        filtered_text = re.sub(r"\s+", " ", filtered_text).strip()

        return filtered_text

    def introduce_track(self, track: dict[str, Any]) -> str:
        """
        Generate introduction for a track.

        Args:
            track: Track dictionary with 'title', 'artist', 'genre', etc.

        Returns:
            Introduction text
        """
        prompt = self._build_intro_prompt(track)
        temperature = self.persona_config.get("temperature", 0.7)

        try:
            response = self.llm_router.generate(prompt, temperature=temperature, max_tokens=150)

            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return self._get_fallback_intro(track)

            intro = self._filter_banned_phrases(response.content)

            # Save to DJ memory
            self.state.add_conversation(role="dj", content=intro)

            return intro

        except Exception as e:
            logger.error(f"Failed to generate track introduction: {e}")
            return self._get_fallback_intro(track)

    def respond_to_listener(self, listener_request: str) -> str:
        """
        Respond to listener requests/comments.

        Args:
            listener_request: Listener's message

        Returns:
            DJ response
        """
        prompt = self._build_response_prompt(listener_request)
        temperature = self.persona_config.get("temperature", 0.7)

        try:
            response = self.llm_router.generate(prompt, temperature=temperature, max_tokens=100)

            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return self._get_fallback_response(listener_request)

            reply = self._filter_banned_phrases(response.content)

            # Save to DJ memory
            self.state.add_conversation(role="listener", content=listener_request)
            self.state.add_conversation(role="dj", content=reply)

            return reply

        except Exception as e:
            logger.error(f"Failed to generate listener response: {e}")
            return self._get_fallback_response(listener_request)

    def generate_transition(self, current_track: dict[str, Any], next_track: dict[str, Any]) -> str:
        """
        Generate smooth transition commentary between tracks.

        Args:
            current_track: Currently playing track
            next_track: Next track to play

        Returns:
            Transition commentary
        """
        prompt = self._build_transition_prompt(current_track, next_track)
        temperature = self.persona_config.get("temperature", 0.7)

        try:
            response = self.llm_router.generate(prompt, temperature=temperature, max_tokens=80)

            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return self._get_fallback_transition(current_track, next_track)

            transition = self._filter_banned_phrases(response.content)

            # Save to DJ memory
            self.state.add_conversation(role="dj", content=transition)

            return transition

        except Exception as e:
            logger.error(f"Failed to generate transition: {e}")
            return self._get_fallback_transition(current_track, next_track)

    def generate_station_id(self) -> str:
        """
        Generate station identification.

        Returns:
            Station ID text
        """
        prompt = (
            f"You're a {self.persona} radio DJ. "
            f"Create a 1-sentence station ID for QFZZ FuzzyRadio. "
            f"Be creative and memorable."
        )
        temperature = self.persona_config.get("temperature", 0.7)

        try:
            response = self.llm_router.generate(prompt, temperature=temperature, max_tokens=50)

            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return "You're listening to QFZZ FuzzyRadio!"

            station_id = self._filter_banned_phrases(response.content)

            # Save to DJ memory
            self.state.add_conversation(role="dj", content=station_id)

            return station_id

        except Exception as e:
            logger.error(f"Failed to generate station ID: {e}")
            return "You're listening to QFZZ FuzzyRadio!"

    def synthesize_speech(self, text: str) -> bytes | None:
        """
        Convert text to speech audio.

        Args:
            text: Text to convert

        Returns:
            Audio data as bytes, or None if TTS is unavailable
        """
        if not self.tts_client:
            logger.debug("TTS client not available")
            return None

        try:
            return self.tts_client.synthesize(text, voice_id=self.voice_id)
        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            return None

    def _build_intro_prompt(self, track: dict[str, Any]) -> str:
        """
        Build prompt for track introduction.

        Args:
            track: Track dictionary

        Returns:
            Prompt text
        """
        persona_prompts = {
            "energetic": "You're an energetic, upbeat radio DJ. Get listeners pumped!",
            "chill": "You're a laid-back, mellow radio DJ. Keep it smooth and relaxed.",
            "intellectual": "You're a knowledgeable, thoughtful DJ who educates listeners.",
            "storyteller": "You're a DJ who tells captivating stories about music.",
        }

        system_prompt = persona_prompts.get(self.persona, persona_prompts["energetic"])

        title = track.get("title", "Unknown Track")
        artist = track.get("artist", "Unknown Artist")
        genre = track.get("genre", "Electronic")

        return (
            f"{system_prompt}\n\n"
            f"Introduce the track '{title}' by {artist} in 1-2 sentences. "
            f"Genre: {genre}. Be engaging!"
        )

    def _build_response_prompt(self, listener_request: str) -> str:
        """
        Build prompt for listener response.

        Args:
            listener_request: Listener's message

        Returns:
            Prompt text
        """
        style = self.persona_config.get("style", "friendly")

        return (
            f"You're a {style} radio DJ named {self.persona_config['name']}. "
            f"A listener said: '{listener_request}'. "
            f"Respond warmly in 1-2 sentences."
        )

    def _build_transition_prompt(self, current: dict[str, Any], next_track: dict[str, Any]) -> str:
        """
        Build prompt for track transition.

        Args:
            current: Current track
            next_track: Next track

        Returns:
            Prompt text
        """
        current_title = current.get("title", "Unknown")
        next_title = next_track.get("title", "Unknown")

        return (
            f"You're a radio DJ. Smoothly transition from '{current_title}' "
            f"to '{next_title}' in one sentence."
        )

    def _get_fallback_intro(self, track: dict[str, Any]) -> str:
        """Get fallback introduction when LLM fails."""
        title = track.get("title", "this track")
        artist = track.get("artist", "Unknown Artist")
        return f"Coming up next, {title} by {artist}!"

    def _get_fallback_response(self, listener_request: str) -> str:
        """Get fallback response when LLM fails."""
        return "Thanks for tuning in! Keep those requests coming!"

    def _get_fallback_transition(self, current: dict[str, Any], next_track: dict[str, Any]) -> str:
        """Get fallback transition when LLM fails."""
        next_title = next_track.get("title", "the next track")
        return f"And now, {next_title}!"

    def get_persona_name(self) -> str:
        """Get the DJ persona's name."""
        return self.persona_config.get("name", "DJ")

    def get_persona_description(self) -> str:
        """Get the DJ persona's description."""
        return self.persona_config.get("description", "")

    def get_available_personas(self) -> list[str]:
        """Get list of available personas."""
        return list(self.personas_config.get("personas", {}).keys())
