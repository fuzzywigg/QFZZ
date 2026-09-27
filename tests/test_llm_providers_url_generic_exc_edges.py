"""HuggingFace URLError and Together generic Exception mapping edges."""

import urllib.error
from unittest.mock import patch

import pytest

from qfzz.exceptions import LLMConnectionError, LLMGenerationError
from qfzz.llm.providers.huggingface_provider import HuggingFaceProvider
from qfzz.llm.providers.together_provider import TogetherProvider


def test_huggingface_urlerror_raises_connection_error():
    provider = HuggingFaceProvider(api_key="hf-test")
    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        side_effect=urllib.error.URLError("dns fail"),
    ):
        with pytest.raises(LLMConnectionError, match="Failed to connect to HuggingFace"):
            provider.generate("hello")


def test_together_unexpected_exception_raises_generation_error():
    provider = TogetherProvider(api_key="tog-test")
    with patch(
        "qfzz.llm.providers.together_provider.urllib.request.urlopen",
        side_effect=RuntimeError("weird parse"),
    ):
        with pytest.raises(LLMGenerationError, match="Together.ai generation error"):
            provider.generate("hello")
