"""Tests for Groq, HuggingFace, and Together LLM providers (mocked HTTP)."""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from qfzz.exceptions import LLMAuthenticationError, LLMConnectionError, LLMGenerationError
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


class TestGroqProvider:
    def test_unavailable_without_key(self):
        provider = GroqProvider(api_key="")
        assert provider.is_available() is False
        with pytest.raises(LLMConnectionError, match="not available"):
            provider.generate("hi")

    def test_generate_success_with_system_prompt(self):
        provider = GroqProvider(api_key="gsk-test", model="mixtral-test")
        resp = _http_response(
            {"choices": [{"message": {"content": "groq says hello"}}]}
        )
        with patch("qfzz.llm.providers.groq_provider.urllib.request.urlopen", return_value=resp):
            text = provider.generate("user prompt", system_prompt="be brief", max_tokens=32)
        assert text == "groq says hello"

    def test_auth_and_rate_limit_errors(self):
        provider = GroqProvider(api_key="gsk-test")
        with patch(
            "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
            side_effect=_http_error(401),
        ):
            with pytest.raises(LLMAuthenticationError):
                provider.generate("x")

        with patch(
            "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
            side_effect=_http_error(429),
        ):
            with pytest.raises(LLMGenerationError, match="rate limit"):
                provider.generate("x")

    def test_connection_error(self):
        import urllib.error

        provider = GroqProvider(api_key="gsk-test")
        with patch(
            "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
            side_effect=urllib.error.URLError("offline"),
        ):
            with pytest.raises(LLMConnectionError, match="Failed to connect"):
                provider.generate("x")


class TestHuggingFaceProvider:
    def test_unavailable_without_key(self):
        provider = HuggingFaceProvider(api_key="")
        assert provider.is_available() is False
        with pytest.raises(LLMConnectionError):
            provider.generate("hi")

    def test_generate_list_response(self):
        provider = HuggingFaceProvider(api_key="hf-test")
        resp = _http_response([{"generated_text": "from list"}])
        with patch(
            "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
            return_value=resp,
        ):
            assert provider.generate("prompt") == "from list"

    def test_generate_dict_response_and_system_prompt(self):
        provider = HuggingFaceProvider(api_key="hf-test")
        resp = _http_response({"generated_text": "from dict"})
        with patch(
            "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
            return_value=resp,
        ) as urlopen:
            text = provider.generate("hello", system_prompt="sys")
            assert text == "from dict"
            req = urlopen.call_args[0][0]
            body = json.loads(req.data.decode("utf-8"))
            assert "[INST]" in body["inputs"]
            assert "sys" in body["inputs"]

    def test_unexpected_format_and_http_errors(self):
        provider = HuggingFaceProvider(api_key="hf-test")
        # json.dumps of a string produces a JSON string; loads returns str.
        with patch(
            "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
            return_value=_http_response("weird"),  # type: ignore[arg-type]
        ):
            with pytest.raises(LLMGenerationError, match="Unexpected response"):
                provider.generate("x")

        with patch(
            "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
            side_effect=_http_error(503),
        ):
            with pytest.raises(LLMGenerationError, match="loading"):
                provider.generate("x")

        with patch(
            "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
            side_effect=_http_error(401),
        ):
            with pytest.raises(LLMAuthenticationError):
                provider.generate("x")


class TestTogetherProvider:
    def test_unavailable_without_key(self):
        provider = TogetherProvider(api_key="")
        assert provider.is_available() is False
        with pytest.raises(LLMConnectionError):
            provider.generate("hi")

    def test_generate_success(self):
        provider = TogetherProvider(api_key="tog-test", model="mistral-test")
        resp = _http_response(
            {"choices": [{"message": {"content": "together reply"}}]}
        )
        with patch(
            "qfzz.llm.providers.together_provider.urllib.request.urlopen",
            return_value=resp,
        ) as urlopen:
            text = provider.generate("user", system_prompt="system", max_tokens=10)
            assert text == "together reply"
            req = urlopen.call_args[0][0]
            body = json.loads(req.data.decode("utf-8"))
            assert "System: system" in body["messages"][0]["content"]
            assert body["max_tokens"] == 10

    def test_http_errors(self):
        provider = TogetherProvider(api_key="tog-test")
        with patch(
            "qfzz.llm.providers.together_provider.urllib.request.urlopen",
            side_effect=_http_error(429),
        ):
            with pytest.raises(LLMGenerationError, match="rate limit"):
                provider.generate("x")

        with patch(
            "qfzz.llm.providers.together_provider.urllib.request.urlopen",
            side_effect=_http_error(500),
        ):
            with pytest.raises(LLMGenerationError, match="API error"):
                provider.generate("x")

        import urllib.error

        with patch(
            "qfzz.llm.providers.together_provider.urllib.request.urlopen",
            side_effect=urllib.error.URLError("down"),
        ):
            with pytest.raises(LLMConnectionError):
                provider.generate("x")
