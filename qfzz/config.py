"""
QFZZ Configuration Module

Centralized configuration management for QFZZ FuzzyRadio.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration for QFZZ."""

    # Station Configuration
    STATION_NAME: str = os.getenv("QFZZ_STATION_NAME", "QFZZ")
    AUDIO_CONTENT_DIR: Path = Path(os.getenv("QFZZ_AUDIO_CONTENT_DIR", "./qfzz_audio_content"))
    CACHE_DIR: Path = Path(os.getenv("QFZZ_CACHE_DIR", "./cache"))
    PORT: int = int(os.getenv("QFZZ_PORT", "8080"))

    # AI/LLM Provider Keys
    GOOGLE_AI_API_KEY: Optional[str] = os.getenv("GOOGLE_AI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    PERPLEXITY_API_KEY: Optional[str] = os.getenv("PERPLEXITY_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")

    # Model Defaults
    GOOGLE_AI_MODEL_DEFAULT: str = os.getenv(
        "GOOGLE_AI_MODEL_DEFAULT", "gemini-2.0-flash-exp"
    )
    CLAUDE_MODEL_DEFAULT: str = os.getenv(
        "CLAUDE_MODEL_DEFAULT", "claude-3-5-sonnet-20241022"
    )
    OPENAI_MODEL_DEFAULT: str = os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini")

    # Ollama (Local)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_DEFAULT: str = os.getenv("OLLAMA_MODEL_DEFAULT", "mistral:7b-instruct")

    # Music Source APIs
    JAMENDO_CLIENT_ID: Optional[str] = os.getenv("JAMENDO_CLIENT_ID")
    INTERNET_ARCHIVE_ACCESS_KEY: Optional[str] = os.getenv("INTERNET_ARCHIVE_ACCESS_KEY")
    INTERNET_ARCHIVE_SECRET_KEY: Optional[str] = os.getenv("INTERNET_ARCHIVE_SECRET_KEY")

    # System Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info").upper()
    ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"

    # Blockchain Configuration
    BLOCKCHAIN_ENABLED: bool = os.getenv("QFZZ_BLOCKCHAIN_ENABLED", "true").lower() == "true"
    LEDGER_FILE: Path = Path(os.getenv("QFZZ_LEDGER_FILE", "./qfzz_ledger.json"))

    # Edge Configuration
    EDGE_MODE: bool = os.getenv("QFZZ_EDGE_MODE", "false").lower() == "true"
    ENABLE_6G: bool = os.getenv("QFZZ_ENABLE_6G", "false").lower() == "true"

    # Advanced Options
    STRICT_LICENSING: bool = os.getenv("QFZZ_STRICT_LICENSING", "true").lower() == "true"
    CACHE_EXPIRY_DAYS: int = int(os.getenv("QFZZ_CACHE_EXPIRY_DAYS", "30"))
    MAX_DOWNLOADS: int = int(os.getenv("QFZZ_MAX_DOWNLOADS", "3"))

    @classmethod
    def is_configured(cls) -> bool:
        """Check if at least one LLM provider is configured."""
        return any([
            cls.GOOGLE_AI_API_KEY,
            cls.ANTHROPIC_API_KEY,
            cls.OPENAI_API_KEY,
            cls.GROQ_API_KEY,
            True  # Ollama is always available (local)
        ])

    @classmethod
    def get_configured_providers(cls) -> list[str]:
        """Get list of configured providers."""
        providers = []
        if cls.GOOGLE_AI_API_KEY:
            providers.append("google")
        if cls.GROQ_API_KEY:
            providers.append("groq")
        if cls.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        if cls.OPENAI_API_KEY:
            providers.append("openai")
        providers.append("ollama")  # Always available
        return providers


# Global config instance
config = Config()
