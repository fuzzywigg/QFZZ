"""Additional HTTP edge cases for Groq / HuggingFace / Together providers."""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from qfzz.exceptions import LLMAuthenticationError, LLMGenerationError
from qfzz.llm.providers.groq_provider import GroqProvider
from qfzz.llm.providers.huggingface_provider import HuggingFaceProvider
from qfzz.llm.providers.together_provider import TogetherProvider


def _http_response(payload: dict | list, status: int = 200) -> MagicMock:
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    resp.status = status
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    return resp


def _http_error(code: int, reason: str = "err"):
    import urllib.error

    return urllib.error.HTTPError(
        url="https://example.test",
        code=code,
        msg=reason,
        hdrs=None,
        fp=BytesIO(b""),
    )


def test_groq_http_500_and_malformed_choices():
    provider = GroqProvider(api_key="gsk-test")
    with patch(
        "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
        side_effect=_http_error(500),
    ):
        with pytest.raises(LLMGenerationError, match="API error"):
            provider.generate("x")

    # missing choices -> KeyError wrapped as LLMGenerationError
    with patch(
        "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
        return_value=_http_response({"choices": []}),
    ):
        with pytest.raises(LLMGenerationError):
            provider.generate("x")

    with patch(
        "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
        return_value=_http_response({"no": "choices"}),
    ):
        with pytest.raises(LLMGenerationError):
            provider.generate("x")


def test_huggingface_non_401_503_and_empty_list():
    provider = HuggingFaceProvider(api_key="hf-test")
    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        side_effect=_http_error(502),
    ):
        with pytest.raises(LLMGenerationError):
            provider.generate("x")

    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        return_value=_http_response([]),
    ):
        with pytest.raises(LLMGenerationError):
            provider.generate("x")


def test_together_auth_401_and_without_system_prompt():
    provider = TogetherProvider(api_key="tog-test")
    with patch(
        "qfzz.llm.providers.together_provider.urllib.request.urlopen",
        side_effect=_http_error(401),
    ):
        with pytest.raises((LLMAuthenticationError, LLMGenerationError)):
            provider.generate("x")

    resp = _http_response({"choices": [{"message": {"content": "plain"}}]})
    with patch(
        "qfzz.llm.providers.together_provider.urllib.request.urlopen",
        return_value=resp,
    ) as urlopen:
        text = provider.generate("user only", max_tokens=8)
        assert text == "plain"
        body = json.loads(urlopen.call_args[0][0].data.decode("utf-8"))
        assert body["messages"][0]["content"] == "user only" or "user only" in body["messages"][0][
            "content"
        ]
