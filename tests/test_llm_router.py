"""Tests for QFZZ LLM Router"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from qfzz.core.llm_router import LLMResponse, LLMRouter


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "test_google_key")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")


@pytest.fixture
def temp_config():
    """Create temporary config file for testing."""
    config_data = {
        "providers": {
            "primary": "google",
            "fallback_chain": ["groq", "anthropic", "openai", "ollama"],
            "cost_optimization": {"prefer_cheap": True, "max_cost_per_request": 0.01},
        },
        "models": {
            "google": "gemini-2.0-flash-exp",
            "anthropic": "claude-3-5-sonnet-20241022",
            "openai": "gpt-4o-mini",
            "groq": "llama-3.1-70b-versatile",
            "ollama": "mistral:7b-instruct",
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def router(mock_env, temp_config):
    """Create LLMRouter with test configuration."""
    return LLMRouter(config_path=temp_config)


class TestLLMRouter:
    """Test LLMRouter class."""

    def test_initialization(self, router):
        """Test router initializes correctly."""
        assert router.config is not None
        assert router.providers is not None
        assert router.request_count == 0
        assert router.total_cost == 0.0

    def test_config_loading(self, router):
        """Test configuration is loaded correctly."""
        assert router.config["providers"]["primary"] == "google"
        assert "groq" in router.config["providers"]["fallback_chain"]
        assert router.config["models"]["google"] == "gemini-2.0-flash-exp"

    def test_provider_initialization(self, router):
        """Test providers are initialized correctly."""
        assert "google" in router.providers
        assert "groq" in router.providers
        assert "anthropic" in router.providers
        assert "openai" in router.providers
        assert "ollama" in router.providers

        # Check API keys are set
        assert router.providers["google"]["api_key"] == "test_google_key"
        assert router.providers["groq"]["api_key"] == "test_groq_key"
        assert router.providers["anthropic"]["api_key"] == "test_anthropic_key"
        assert router.providers["openai"]["api_key"] == "test_openai_key"

    def test_provider_availability(self, router):
        """Test provider availability flags."""
        assert router.providers["google"]["available"] is True
        assert router.providers["groq"]["available"] is True
        assert router.providers["anthropic"]["available"] is True
        assert router.providers["openai"]["available"] is True
        assert router.providers["ollama"]["available"] is True

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_google_provider_success(self, mock_model_class, mock_configure, router):
        """Test successful Google Gemini call."""
        # Mock the Google API
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated response from Gemini"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # Make request
        response = router._call_google("Test prompt")

        # Verify response
        assert response.success is True
        assert response.provider == "google"
        assert response.content == "Generated response from Gemini"
        assert response.cost >= 0

    @patch("qfzz.core.llm_router.requests.post")
    def test_groq_provider_success(self, mock_post, router):
        """Test successful Groq call."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response from Groq"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Make request
        response = router._call_groq("Test prompt")

        # Verify response
        assert response.success is True
        assert response.provider == "groq"
        assert response.content == "Response from Groq"
        assert response.cost == 0.0  # Groq is free

    @patch("anthropic.Anthropic")
    def test_anthropic_provider_success(self, mock_anthropic, router):
        """Test successful Anthropic Claude call."""
        # Mock the API
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Response from Claude"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        # Make request
        response = router._call_anthropic("Test prompt")

        # Verify response
        assert response.success is True
        assert response.provider == "anthropic"
        assert response.content == "Response from Claude"

    @patch("openai.OpenAI")
    def test_openai_provider_success(self, mock_openai, router):
        """Test successful OpenAI call."""
        # Mock the API
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Response from OpenAI"
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Make request
        response = router._call_openai("Test prompt")

        # Verify response
        assert response.success is True
        assert response.provider == "openai"
        assert response.content == "Response from OpenAI"

    @patch("qfzz.core.llm_router.requests.post")
    def test_ollama_provider_success(self, mock_post, router):
        """Test successful Ollama call."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Response from Ollama"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Make request
        response = router._call_ollama("Test prompt")

        # Verify response
        assert response.success is True
        assert response.provider == "ollama"
        assert response.content == "Response from Ollama"
        assert response.cost == 0.0  # Local, no cost

    def test_provider_failure(self, router):
        """Test provider failure handling."""
        # Call with invalid configuration (should fail)
        with patch("google.generativeai.configure") as mock_config:
            mock_config.side_effect = Exception("API Error")

            response = router._call_google("Test prompt")

            assert response.success is False
            assert response.error is not None

    @patch.object(LLMRouter, "_call_google")
    def test_fallback_chain(self, mock_google, router):
        """Test fallback chain when primary provider fails."""
        # Make primary provider fail
        mock_google.return_value = LLMResponse(
            content="",
            provider="google",
            model="gemini-2.0-flash-exp",
            cost=0.0,
            latency=0.0,
            success=False,
            error="API Error",
        )

        # Mock successful fallback
        with patch.object(router, "_call_groq") as mock_groq:
            mock_groq.return_value = LLMResponse(
                content="Fallback response",
                provider="groq",
                model="llama-3.1-70b-versatile",
                cost=0.0,
                latency=0.5,
                success=True,
            )

            # Make request
            response = router.generate("Test prompt")

            # Should have fallen back to Groq
            assert response.success is True
            assert response.provider == "groq"
            assert response.content == "Fallback response"

    @patch.object(LLMRouter, "_call_google")
    @patch.object(LLMRouter, "_call_groq")
    @patch.object(LLMRouter, "_call_anthropic")
    @patch.object(LLMRouter, "_call_openai")
    @patch.object(LLMRouter, "_call_ollama")
    def test_all_providers_fail(
        self, mock_ollama, mock_openai, mock_anthropic, mock_groq, mock_google, router
    ):
        """Test behavior when all providers fail."""
        # Make all providers fail
        for mock_provider in [mock_google, mock_groq, mock_anthropic, mock_openai, mock_ollama]:
            mock_provider.return_value = LLMResponse(
                content="",
                provider="",
                model="",
                cost=0.0,
                latency=0.0,
                success=False,
                error="Failed",
            )

        # Make request
        response = router.generate("Test prompt")

        # Should fail
        assert response.success is False
        assert "All providers failed" in response.error

    @patch.object(LLMRouter, "_call_groq")
    def test_preferred_provider(self, mock_groq, router):
        """Test using preferred provider override."""
        mock_groq.return_value = LLMResponse(
            content="Groq response",
            provider="groq",
            model="llama-3.1-70b-versatile",
            cost=0.0,
            latency=0.5,
            success=True,
        )

        # Request with preferred provider
        response = router.generate("Test prompt", preferred_provider="groq")

        # Should use Groq first
        assert response.success is True
        assert response.provider == "groq"

    def test_stats_tracking(self, router):
        """Test request and cost tracking."""
        # Mock successful call
        with patch.object(router, "_call_google") as mock_google:
            mock_google.return_value = LLMResponse(
                content="Test response",
                provider="google",
                model="gemini-2.0-flash-exp",
                cost=0.001,
                latency=0.5,
                success=True,
            )

            # Make multiple requests
            router.generate("Test 1")
            router.generate("Test 2")
            router.generate("Test 3")

            # Check stats
            stats = router.get_stats()
            assert stats["total_requests"] == 3
            assert stats["total_cost"] == 0.003
            assert stats["average_cost"] == 0.001
            assert "google" in stats["available_providers"]

    def test_default_config_when_file_missing(self, mock_env):
        """Test router uses default config when file is missing."""
        router = LLMRouter(config_path="nonexistent.json")

        # Should still work with default config
        assert router.config is not None
        assert router.config["providers"]["primary"] == "google"


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_response_creation(self):
        """Test creating LLMResponse."""
        response = LLMResponse(
            content="Test content",
            provider="test_provider",
            model="test_model",
            cost=0.001,
            latency=0.5,
            success=True,
        )

        assert response.content == "Test content"
        assert response.provider == "test_provider"
        assert response.model == "test_model"
        assert response.cost == 0.001
        assert response.latency == 0.5
        assert response.success is True
        assert response.error is None

    def test_response_with_error(self):
        """Test creating LLMResponse with error."""
        response = LLMResponse(
            content="",
            provider="test_provider",
            model="test_model",
            cost=0.0,
            latency=0.0,
            success=False,
            error="Test error",
        )

        assert response.success is False
        assert response.error == "Test error"
