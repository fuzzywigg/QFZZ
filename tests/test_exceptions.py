"""Tests for the QFZZ exception hierarchy."""

import pytest

from qfzz.exceptions import (
    AudioAnalysisError,
    AudioProcessingError,
    ConfigurationError,
    LLMAuthenticationError,
    LLMProviderError,
    QFZZException,
)


def test_base_exception_message_and_details():
    err = QFZZException("boom", details={"code": 42})
    assert err.message == "boom"
    assert err.details == {"code": 42}
    assert "boom" in str(err)
    assert "code=42" in str(err)


def test_base_exception_without_details():
    err = QFZZException("plain")
    assert str(err) == "plain"
    assert err.details == {}


def test_exception_inheritance():
    assert issubclass(AudioAnalysisError, AudioProcessingError)
    assert issubclass(AudioProcessingError, QFZZException)
    assert issubclass(LLMAuthenticationError, LLMProviderError)
    assert issubclass(ConfigurationError, QFZZException)


def test_raise_and_catch_as_base():
    with pytest.raises(QFZZException) as exc_info:
        raise AudioAnalysisError("bad sample", details={"path": "x.wav"})
    assert exc_info.value.details["path"] == "x.wav"
