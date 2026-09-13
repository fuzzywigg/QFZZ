"""HuggingFaceProvider URLError → LLMConnectionError edge."""

import urllib.error
from unittest.mock import patch

import pytest

from qfzz.exceptions import LLMConnectionError
from qfzz.llm.providers.huggingface_provider import HuggingFaceProvider


def test_hf_urlerror_raises_connection_error():
    provider = HuggingFaceProvider(api_key="hf-test")
    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        side_effect=urllib.error.URLError("offline"),
    ):
        with pytest.raises(LLMConnectionError, match="Failed to connect to HuggingFace"):
            provider.generate("prompt")
