"""HuggingFace system_prompt wrapping + 429/503 HTTP edges."""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from qfzz.exceptions import LLMGenerationError
from qfzz.llm.providers.huggingface_provider import HuggingFaceProvider


def _ok(payload):
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    return resp


def _http_error(code: int):
    import urllib.error

    return urllib.error.HTTPError(
        url="https://example.test",
        code=code,
        msg="err",
        hdrs=None,
        fp=BytesIO(b""),
    )


def test_system_prompt_wraps_inst_tags():
    provider = HuggingFaceProvider(api_key="hf-test")
    captured = {}

    def fake_urlopen(req, timeout=60):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _ok([{"generated_text": "ok"}])

    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        side_effect=fake_urlopen,
    ):
        text = provider.generate("user-q", system_prompt="sys-role")

    assert text == "ok"
    prompt = captured["body"]["inputs"]
    assert prompt.startswith("[INST] sys-role")
    assert "user-q" in prompt
    assert prompt.endswith("[/INST]")


def test_http_429_and_503_raise_generation_error():
    provider = HuggingFaceProvider(api_key="hf-test")
    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        side_effect=_http_error(429),
    ):
        with pytest.raises(LLMGenerationError, match="rate limit"):
            provider.generate("x")

    with patch(
        "qfzz.llm.providers.huggingface_provider.urllib.request.urlopen",
        side_effect=_http_error(503),
    ):
        with pytest.raises(LLMGenerationError, match="loading"):
            provider.generate("x")
