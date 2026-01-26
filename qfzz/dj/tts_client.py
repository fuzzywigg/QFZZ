"""
Text-to-Speech Client for QFZZ AI DJ.

Supports multiple TTS providers including OpenAI, ElevenLabs, and Google Cloud TTS.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class TTSClient:
    """Text-to-speech client supporting multiple providers."""

    def __init__(self, provider: str = "openai"):
        """
        Initialize TTS client.

        Args:
            provider: TTS provider ('openai', 'elevenlabs', 'google')
        """
        self.provider = provider.lower()
        self._client = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the TTS provider based on configuration."""
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "elevenlabs":
            self._initialize_elevenlabs()
        elif self.provider == "google":
            self._initialize_google()
        else:
            logger.warning(f"Unknown TTS provider: {self.provider}, defaulting to OpenAI")
            self.provider = "openai"
            self._initialize_openai()

    def _initialize_openai(self):
        """Initialize OpenAI TTS client."""
        try:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OpenAI API key not found. TTS will be unavailable.")
                self._client = None
                return

            self._client = OpenAI(api_key=api_key)
            logger.info("OpenAI TTS client initialized")
        except ImportError:
            logger.warning("OpenAI library not installed. TTS will be unavailable.")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI TTS: {e}")
            self._client = None

    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs TTS client."""
        try:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                logger.warning("ElevenLabs API key not found. TTS will be unavailable.")
                self._client = None
                return

            # Store API key for later use
            self._client = {"api_key": api_key}
            logger.info("ElevenLabs TTS client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs TTS: {e}")
            self._client = None

    def _initialize_google(self):
        """Initialize Google Cloud TTS client."""
        try:
            from google.cloud import texttospeech

            self._client = texttospeech.TextToSpeechClient()
            logger.info("Google Cloud TTS client initialized")
        except ImportError:
            logger.warning("Google Cloud TTS library not installed. TTS will be unavailable.")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud TTS: {e}")
            self._client = None

    def synthesize(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize speech from text.

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (provider-specific)

        Returns:
            Audio data as bytes, or None if synthesis fails
        """
        if not self._client:
            logger.warning("TTS client not initialized. Cannot synthesize speech.")
            return None

        try:
            if self.provider == "openai":
                return self._synthesize_openai(text, voice_id or "alloy")
            elif self.provider == "elevenlabs":
                return self._synthesize_elevenlabs(text, voice_id)
            elif self.provider == "google":
                return self._synthesize_google(text, voice_id)
        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            return None

        return None

    def _synthesize_openai(self, text: str, voice: str) -> bytes:
        """
        Synthesize speech using OpenAI TTS.

        Args:
            text: Text to convert
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            Audio data in MP3 format
        """
        response = self._client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )

        return response.content

    def _synthesize_elevenlabs(self, text: str, voice_id: Optional[str]) -> bytes:
        """
        Synthesize speech using ElevenLabs API.

        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID

        Returns:
            Audio data
        """
        import requests

        # Default voice if none provided
        if not voice_id:
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self._client["api_key"],
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        return response.content

    def _synthesize_google(self, text: str, voice_id: Optional[str]) -> bytes:
        """
        Synthesize speech using Google Cloud TTS.

        Args:
            text: Text to convert
            voice_id: Google voice name

        Returns:
            Audio data
        """
        from google.cloud import texttospeech

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        if voice_id:
            voice = texttospeech.VoiceSelectionParams(
                name=voice_id, language_code="en-US"
            )
        else:
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            )

        # Select the type of audio file
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request
        response = self._client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        return response.audio_content

    def is_available(self) -> bool:
        """
        Check if TTS client is available.

        Returns:
            True if client is initialized, False otherwise
        """
        return self._client is not None

    def get_available_voices(self) -> list[str]:
        """
        Get list of available voices for the current provider.

        Returns:
            List of voice identifiers
        """
        if self.provider == "openai":
            return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        elif self.provider == "elevenlabs":
            # Would need to query API for available voices
            return ["21m00Tcm4TlvDq8ikWAM"]  # Rachel default
        elif self.provider == "google":
            # Would need to query API for available voices
            return ["en-US-Neural2-C", "en-US-Neural2-D"]
        return []
