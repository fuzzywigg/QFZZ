"""TogetherProvider bare Exception during response read → LLMGenerationError."""

from unittest.mock import MagicMock, patch

import pytest

from qfzz.exceptions import LLMGenerationError
from qfzz.llm.providers.together_provider import TogetherProvider


def test_together_generic_exception_raises_generation_error():
    provider = TogetherProvider(api_key="tog-test")
    resp = MagicMock()
    resp.read.side_effect = RuntimeError("truncated body")
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False

    with patch(
        "qfzz.llm.providers.together_provider.urllib.request.urlopen",
        return_value=resp,
    ):
        with pytest.raises(LLMGenerationError, match="Together.ai generation error"):
            provider.generate("x")
