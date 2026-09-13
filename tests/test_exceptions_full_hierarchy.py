"""Full leaf coverage for the QFZZ exception hierarchy."""

import pytest

from qfzz import exceptions as ex

LEAF_CLASSES = [
    ex.AudioAnalysisError,
    ex.AudioGenerationError,
    ex.AudioFormatError,
    ex.LLMConnectionError,
    ex.LLMGenerationError,
    ex.LLMAuthenticationError,
    ex.LLMRateLimitError,
    ex.DatasetLoadError,
    ex.DatasetValidationError,
    ex.DatasetNotFoundError,
    ex.DatasetLicenseError,
    ex.StreamConnectionError,
    ex.StreamBufferError,
    ex.StreamFormatError,
    ex.MusicSourceConnectionError,
    ex.MusicSourceAuthError,
    ex.MusicSourceNotFoundError,
    ex.MusicSourceRateLimitError,
    ex.BlockchainValidationError,
    ex.BlockchainSyncError,
    ex.ConfigurationValidationError,
    ex.ConfigurationMissingError,
    ex.CacheReadError,
    ex.CacheWriteError,
    ex.CacheCorruptedError,
    ex.NetworkTimeoutError,
    ex.NetworkConnectionError,
]


@pytest.mark.parametrize("cls", LEAF_CLASSES)
def test_leaf_exception_mro_and_str(cls):
    err = cls("edge", details={"k": "v"})
    assert isinstance(err, ex.QFZZException)
    assert err.message == "edge"
    assert "k=v" in str(err)
    plain = cls("plain")
    assert str(plain) == "plain"
    assert plain.details == {}


def test_mid_level_bases():
    assert issubclass(ex.AudioProcessingError, ex.QFZZException)
    assert issubclass(ex.LLMProviderError, ex.QFZZException)
    assert issubclass(ex.DatasetError, ex.QFZZException)
    assert issubclass(ex.StreamingError, ex.QFZZException)
    assert issubclass(ex.MusicSourceError, ex.QFZZException)
    assert issubclass(ex.BlockchainError, ex.QFZZException)
    assert issubclass(ex.CacheError, ex.QFZZException)
    assert issubclass(ex.NetworkError, ex.QFZZException)
