"""GeminiClient successful configure path (mocked google.generativeai)."""

from unittest.mock import MagicMock, patch

from qfzz.llm.client import GeminiClient


def test_gemini_init_success_marks_available():
    fake_genai = MagicMock()
    fake_model = MagicMock()
    fake_genai.GenerativeModel.return_value = fake_model

    with patch.dict("sys.modules", {"google.generativeai": fake_genai}):
        # Ensure import resolves to our fake
        with patch("google.generativeai", fake_genai, create=True):
            client = GeminiClient(api_key="sk-test", model="gemini-pro")

    assert client.is_available() is True
    fake_genai.configure.assert_called_once_with(api_key="sk-test")
    fake_genai.GenerativeModel.assert_called_once_with("gemini-pro")
    assert client.model is fake_model
