"""
Configuration management for QFZZ.
Centralizes all configuration with environment variable support.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class StationSettings:
    """Station-level configuration."""

    name: str = "QFZZ"
    audio_content_dir: str = "./qfzz_audio_content"
    cache_dir: str = "./cache"
    port: int = 8080
    edge_mode: bool = False
    enable_6g: bool = False
    blockchain_enabled: bool = True
    ledger_file: str = "./qfzz_ledger.json"


@dataclass
class LLMSettings:
    """LLM provider configuration."""

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    together_api_key: str | None = None
    huggingface_api_key: str | None = None


@dataclass
class MusicSourceSettings:
    """Music source API configuration."""

    jamendo_client_id: str | None = None
    internet_archive_access_key: str | None = None
    internet_archive_secret_key: str | None = None


@dataclass
class LoggingSettings:
    """Logging configuration."""

    level: str = "INFO"
    file: str = "./logs/qfzz.log"


@dataclass
class AdvancedSettings:
    """Advanced configuration options."""

    strict_licensing: bool = True
    cache_expiry_days: int = 30
    max_downloads: int = 3


@dataclass
class QFZZSettings:
    """Main QFZZ configuration."""

    station: StationSettings = field(default_factory=StationSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    music_sources: MusicSourceSettings = field(default_factory=MusicSourceSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    advanced: AdvancedSettings = field(default_factory=AdvancedSettings)


class ConfigManager:
    """Manages QFZZ configuration from multiple sources."""

    def __init__(self, config_file: str | None = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to YAML config file (optional)
        """
        self.config_file = config_file or self._find_config_file()
        self._settings: QFZZSettings | None = None
        self._load_config()

    def _find_config_file(self) -> str | None:
        """Find configuration file in standard locations."""
        search_paths = [
            "config/default.yaml",
            "config/config.yaml",
            os.path.expanduser("~/.qfzz/config.yaml"),
        ]

        for path in search_paths:
            if os.path.exists(path):
                logger.info(f"Found configuration file: {path}")
                return path

        return None

    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Start with defaults
        settings = QFZZSettings()

        # Load from YAML file if available
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file) as f:
                    yaml_config = yaml.safe_load(f) or {}
                self._apply_yaml_config(settings, yaml_config)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")

        # Override with environment variables
        self._apply_env_config(settings)

        # Validate configuration
        self._validate_config(settings)

        self._settings = settings

    def _apply_yaml_config(self, settings: QFZZSettings, yaml_config: dict[str, Any]):
        """Apply YAML configuration to settings."""
        # Station settings
        if "station" in yaml_config:
            station = yaml_config["station"]
            for key, value in station.items():
                if hasattr(settings.station, key):
                    setattr(settings.station, key, value)

        # LLM settings
        if "llm" in yaml_config:
            llm = yaml_config["llm"]
            for key, value in llm.items():
                if hasattr(settings.llm, key):
                    setattr(settings.llm, key, value)

        # Music source settings
        if "music_sources" in yaml_config:
            music = yaml_config["music_sources"]
            for key, value in music.items():
                if hasattr(settings.music_sources, key):
                    setattr(settings.music_sources, key, value)

        # Logging settings
        if "logging" in yaml_config:
            logging_cfg = yaml_config["logging"]
            for key, value in logging_cfg.items():
                if hasattr(settings.logging, key):
                    setattr(settings.logging, key, value)

        # Advanced settings
        if "advanced" in yaml_config:
            advanced = yaml_config["advanced"]
            for key, value in advanced.items():
                if hasattr(settings.advanced, key):
                    setattr(settings.advanced, key, value)

    def _apply_env_config(self, settings: QFZZSettings):
        """Apply environment variable configuration to settings."""
        # Station settings
        settings.station.name = os.getenv("QFZZ_STATION_NAME", settings.station.name)
        settings.station.audio_content_dir = os.getenv(
            "QFZZ_AUDIO_CONTENT_DIR", settings.station.audio_content_dir
        )
        settings.station.cache_dir = os.getenv("QFZZ_CACHE_DIR", settings.station.cache_dir)
        settings.station.port = int(os.getenv("QFZZ_PORT", str(settings.station.port)))
        settings.station.edge_mode = os.getenv("QFZZ_EDGE_MODE", "").lower() == "true"
        settings.station.enable_6g = os.getenv("QFZZ_ENABLE_6G", "").lower() == "true"
        settings.station.blockchain_enabled = (
            os.getenv("QFZZ_BLOCKCHAIN_ENABLED", "true").lower() == "true"
        )
        settings.station.ledger_file = os.getenv("QFZZ_LEDGER_FILE", settings.station.ledger_file)

        # LLM settings
        settings.llm.ollama_base_url = os.getenv("OLLAMA_BASE_URL", settings.llm.ollama_base_url)
        settings.llm.ollama_model = os.getenv("OLLAMA_MODEL", settings.llm.ollama_model)
        settings.llm.gemini_api_key = os.getenv("GEMINI_API_KEY", settings.llm.gemini_api_key)
        settings.llm.groq_api_key = os.getenv("GROQ_API_KEY", settings.llm.groq_api_key)
        settings.llm.together_api_key = os.getenv("TOGETHER_API_KEY", settings.llm.together_api_key)
        settings.llm.huggingface_api_key = os.getenv(
            "HUGGINGFACE_API_KEY", settings.llm.huggingface_api_key
        )

        # Music source settings
        settings.music_sources.jamendo_client_id = os.getenv(
            "JAMENDO_CLIENT_ID", settings.music_sources.jamendo_client_id
        )
        settings.music_sources.internet_archive_access_key = os.getenv(
            "INTERNET_ARCHIVE_ACCESS_KEY", settings.music_sources.internet_archive_access_key
        )
        settings.music_sources.internet_archive_secret_key = os.getenv(
            "INTERNET_ARCHIVE_SECRET_KEY", settings.music_sources.internet_archive_secret_key
        )

        # Logging settings
        settings.logging.level = os.getenv("QFZZ_LOG_LEVEL", settings.logging.level)
        settings.logging.file = os.getenv("QFZZ_LOG_FILE", settings.logging.file)

        # Advanced settings
        settings.advanced.strict_licensing = (
            os.getenv("QFZZ_STRICT_LICENSING", "true").lower() == "true"
        )
        settings.advanced.cache_expiry_days = int(
            os.getenv("QFZZ_CACHE_EXPIRY_DAYS", str(settings.advanced.cache_expiry_days))
        )
        settings.advanced.max_downloads = int(
            os.getenv("QFZZ_MAX_DOWNLOADS", str(settings.advanced.max_downloads))
        )

    def _validate_config(self, settings: QFZZSettings):
        """Validate configuration settings."""
        # Create necessary directories
        os.makedirs(settings.station.audio_content_dir, exist_ok=True)
        os.makedirs(settings.station.cache_dir, exist_ok=True)

        # Create log directory
        log_dir = os.path.dirname(settings.logging.file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Validate port
        if not (1024 <= settings.station.port <= 65535):
            logger.warning(f"Invalid port {settings.station.port}, using default 8080")
            settings.station.port = 8080

    def get_settings(self) -> QFZZSettings:
        """Get current configuration settings."""
        if self._settings is None:
            self._load_config()
        return self._settings

    def reload(self):
        """Reload configuration from sources."""
        self._load_config()


# Global configuration instance
_config_manager: ConfigManager | None = None


def get_config() -> QFZZSettings:
    """Get global configuration instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_settings()


def reload_config():
    """Reload global configuration."""
    global _config_manager
    if _config_manager:
        _config_manager.reload()
    else:
        _config_manager = ConfigManager()
