"""core LLMRouter _call_google exception → success=False."""

import builtins
from unittest.mock import patch

from qfzz.core.llm_router import LLMRouter


def test_call_google_exception_returns_failure(temp_config, monkeypatch):
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "sk-test-google")
    router = LLMRouter(config_path=temp_config)
    router.providers["google"]["available"] = True
    router.providers["google"]["api_key"] = "sk-test-google"
    router.providers["google"]["model"] = "gemini-test"

    real_import = builtins.__import__

    def boom_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "google.generativeai" or (
            name == "google" and fromlist and "generativeai" in fromlist
        ):
            raise RuntimeError("gemini down")
        return real_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=boom_import):
        response = router._call_google("hi")

    assert response.success is False
    assert response.provider == "google"
    assert "gemini down" in (response.error or "")
