"""
QFZZ Exception Hierarchy.
Provides structured error handling throughout the application.
"""


class QFZZException(Exception):
    """Base exception for all QFZZ errors."""
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize QFZZ exception.
        
        Args:
            message: Error message
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class AudioProcessingError(QFZZException):
    """Raised when audio processing fails."""
    pass


class AudioAnalysisError(AudioProcessingError):
    """Raised when audio analysis fails (e.g., librosa operations)."""
    pass


class AudioGenerationError(AudioProcessingError):
    """Raised when audio generation fails."""
    pass


class AudioFormatError(AudioProcessingError):
    """Raised when audio format is invalid or unsupported."""
    pass


class LLMProviderError(QFZZException):
    """Base class for LLM provider errors."""
    pass


class LLMConnectionError(LLMProviderError):
    """Raised when connection to LLM provider fails."""
    pass


class LLMGenerationError(LLMProviderError):
    """Raised when LLM text generation fails."""
    pass


class LLMAuthenticationError(LLMProviderError):
    """Raised when LLM provider authentication fails."""
    pass


class LLMRateLimitError(LLMProviderError):
    """Raised when LLM provider rate limit is exceeded."""
    pass


class DatasetError(QFZZException):
    """Base class for dataset-related errors."""
    pass


class DatasetLoadError(DatasetError):
    """Raised when dataset loading fails."""
    pass


class DatasetValidationError(DatasetError):
    """Raised when dataset validation fails."""
    pass


class DatasetNotFoundError(DatasetError):
    """Raised when requested dataset is not found."""
    pass


class DatasetLicenseError(DatasetError):
    """Raised when dataset license is invalid or incompatible."""
    pass


class StreamingError(QFZZException):
    """Base class for streaming-related errors."""
    pass


class StreamConnectionError(StreamingError):
    """Raised when streaming connection fails."""
    pass


class StreamBufferError(StreamingError):
    """Raised when streaming buffer issues occur."""
    pass


class StreamFormatError(StreamingError):
    """Raised when stream format is invalid."""
    pass


class MusicSourceError(QFZZException):
    """Base class for music source errors."""
    pass


class MusicSourceConnectionError(MusicSourceError):
    """Raised when connection to music source fails."""
    pass


class MusicSourceAuthError(MusicSourceError):
    """Raised when music source authentication fails."""
    pass


class MusicSourceNotFoundError(MusicSourceError):
    """Raised when requested content is not found in music source."""
    pass


class MusicSourceRateLimitError(MusicSourceError):
    """Raised when music source rate limit is exceeded."""
    pass


class BlockchainError(QFZZException):
    """Base class for blockchain-related errors."""
    pass


class BlockchainValidationError(BlockchainError):
    """Raised when blockchain validation fails."""
    pass


class BlockchainSyncError(BlockchainError):
    """Raised when blockchain synchronization fails."""
    pass


class ConfigurationError(QFZZException):
    """Raised when configuration is invalid or missing."""
    pass


class ConfigurationValidationError(ConfigurationError):
    """Raised when configuration validation fails."""
    pass


class ConfigurationMissingError(ConfigurationError):
    """Raised when required configuration is missing."""
    pass


class CacheError(QFZZException):
    """Base class for cache-related errors."""
    pass


class CacheReadError(CacheError):
    """Raised when reading from cache fails."""
    pass


class CacheWriteError(CacheError):
    """Raised when writing to cache fails."""
    pass


class CacheCorruptedError(CacheError):
    """Raised when cached data is corrupted."""
    pass


class NetworkError(QFZZException):
    """Base class for network-related errors."""
    pass


class NetworkTimeoutError(NetworkError):
    """Raised when network request times out."""
    pass


class NetworkConnectionError(NetworkError):
    """Raised when network connection fails."""
    pass
