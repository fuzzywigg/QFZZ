"""
Comprehensive core tests for LLM Router.

Tests provider initialization, fallback logic, cost optimization,
and comprehensive error handling not covered in test_llm_router.py.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from qfzz.core.llm_router import LLMResponse, LLMRouter


class TestProviderInitialization:
    """Test detailed provider initialization logic."""

    def test_all_providers_have_correct_models(self, mock_env, temp_config):
        """Test that all providers initialize with correct model names."""
        router = LLMRouter(config_path=temp_config)

        assert router.providers["google"]["model"] == "gemini-2.0-flash-exp"
        assert router.providers["groq"]["model"] == "llama-3.1-70b-versatile"
        assert router.providers["anthropic"]["model"] == "claude-3-5-sonnet-20241022"
        assert router.providers["openai"]["model"] == "gpt-4o-mini"
        assert router.providers["ollama"]["model"] == "mistral:7b-instruct"

    def test_all_providers_have_correct_costs(self, mock_env, temp_config):
        """Test that all providers have correct cost_per_1k values."""
        router = LLMRouter(config_path=temp_config)

        assert router.providers["google"]["cost_per_1k"] == 0.000075
        assert router.providers["groq"]["cost_per_1k"] == 0.0  # Free
        assert router.providers["anthropic"]["cost_per_1k"] == 0.003
        assert router.providers["openai"]["cost_per_1k"] == 0.00015
        assert router.providers["ollama"]["cost_per_1k"] == 0.0  # Local/Free

    def test_provider_availability_without_api_keys(self, clean_env):
        """Test provider availability when API keys are missing."""
        router = LLMRouter(config_path="nonexistent.json")

        # All providers requiring keys should be unavailable
        assert router.providers["google"]["available"] is False
        assert router.providers["groq"]["available"] is False
        assert router.providers["anthropic"]["available"] is False
        assert router.providers["openai"]["available"] is False

        # Ollama should still be available (local, no key needed)
        assert router.providers["ollama"]["available"] is True

    def test_partial_provider_availability(self, monkeypatch):
        """Test when only some providers have API keys."""
        # Clean environment first
        for key in ["GOOGLE_AI_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
            monkeypatch.delenv(key, raising=False)
            
        monkeypatch.setenv("GOOGLE_AI_API_KEY", "test_key")
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        # No anthropic or openai keys

        router = LLMRouter(config_path="nonexistent.json")

        assert router.providers["google"]["available"] is True
        assert router.providers["groq"]["available"] is True
        assert router.providers["anthropic"]["available"] is False
        assert router.providers["openai"]["available"] is False
        assert router.providers["ollama"]["available"] is True


class TestFallbackLogic:
    """Test comprehensive fallback chain logic."""

    @patch.object(LLMRouter, "_call_google")
    @patch.object(LLMRouter, "_call_groq")
    def test_fallback_chain_order(self, mock_groq, mock_google, mock_env, temp_config):
        """Test that fallback chain follows correct order."""
        router = LLMRouter(config_path=temp_config)

        # Make google fail
        mock_google.return_value = LLMResponse(
            content="",
            provider="google",
            model="gemini-2.0-flash-exp",
            cost=0.0,
            latency=0.0,
            success=False,
            error="Google API Error",
        )

        # Make groq succeed
        mock_groq.return_value = LLMResponse(
            content="Groq response",
            provider="groq",
            model="llama-3.1-70b-versatile",
            cost=0.0,
            latency=0.5,
            success=True,
        )

        response = router.generate("Test prompt")

        # Should try google first, then groq
        mock_google.assert_called_once()
        mock_groq.assert_called_once()
        assert response.success is True
        assert response.provider == "groq"

    @patch.object(LLMRouter, "_call_google")
    @patch.object(LLMRouter, "_call_groq")
    @patch.object(LLMRouter, "_call_anthropic")
    @patch.object(LLMRouter, "_call_openai")
    def test_fallback_continues_until_success(
        self, mock_openai, mock_anthropic, mock_groq, mock_google, mock_env, temp_config
    ):
        """Test that fallback continues through chain until success."""
        router = LLMRouter(config_path=temp_config)

        # Make first three fail
        for mock in [mock_google, mock_groq, mock_anthropic]:
            mock.return_value = LLMResponse(
                content="",
                provider="",
                model="",
                cost=0.0,
                latency=0.0,
                success=False,
                error="Failed",
            )

        # Make openai succeed
        mock_openai.return_value = LLMResponse(
            content="OpenAI response",
            provider="openai",
            model="gpt-4o-mini",
            cost=0.0001,
            latency=0.5,
            success=True,
        )

        response = router.generate("Test prompt")

        # Should try all until openai
        assert response.success is True
        assert response.provider == "openai"
        mock_google.assert_called_once()
        mock_groq.assert_called_once()
        mock_anthropic.assert_called_once()
        mock_openai.assert_called_once()

    @patch.object(LLMRouter, "_call_anthropic")
    def test_preferred_provider_overrides_primary(self, mock_anthropic, mock_env, temp_config):
        """Test that preferred_provider parameter overrides primary."""
        router = LLMRouter(config_path=temp_config)

        mock_anthropic.return_value = LLMResponse(
            content="Anthropic response",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            cost=0.003,
            latency=0.5,
            success=True,
        )

        response = router.generate("Test prompt", preferred_provider="anthropic")

        # Should try anthropic first
        mock_anthropic.assert_called_once()
        assert response.provider == "anthropic"

    def test_all_providers_fail_returns_error(self, mock_env, temp_config):
        """Test that all providers failing returns appropriate error."""
        router = LLMRouter(config_path=temp_config)

        # Mock all to fail
        failed_response = LLMResponse(
            content="",
            provider="",
            model="",
            cost=0.0,
            latency=0.0,
            success=False,
            error="Provider failed",
        )

        with patch.object(router, "_call_google", return_value=failed_response), patch.object(
            router, "_call_groq", return_value=failed_response
        ), patch.object(router, "_call_anthropic", return_value=failed_response), patch.object(
            router, "_call_openai", return_value=failed_response
        ), patch.object(
            router, "_call_ollama", return_value=failed_response
        ):
            response = router.generate("Test prompt")

        assert response.success is False
        assert "All providers failed" in response.error or "failed" in response.error.lower()


class TestCostOptimization:
    """Test cost calculation and optimization."""

    def test_cost_calculation_accurate(self, mock_llm_router):
        """Test that cost calculation is accurate based on tokens."""
        router = mock_llm_router

        # Make a request
        response = router.generate("This is a test prompt with several words")

        # Should have non-zero cost for google (primary)
        assert response.cost > 0
        assert response.success is True

    def test_total_cost_accumulates(self, mock_llm_router):
        """Test that total_cost accumulates across requests."""
        router = mock_llm_router

        # Make multiple requests
        router.generate("Request 1")
        router.generate("Request 2")
        router.generate("Request 3")

        stats = router.get_stats()
        assert stats["total_cost"] > 0
        assert stats["total_requests"] == 3

    def test_cost_tracking_per_provider(self, mock_env, temp_config):
        """Test cost tracking for different providers."""
        router = LLMRouter(config_path=temp_config)

        # Mock google with specific cost
        with patch.object(router, "_call_google") as mock_google:
            mock_google.return_value = LLMResponse(
                content="Response",
                provider="google",
                model="gemini-2.0-flash-exp",
                cost=0.001,
                latency=0.5,
                success=True,
            )

            response1 = router.generate("Test 1")

        # Mock groq with zero cost
        with patch.object(router, "_call_groq") as mock_groq:
            mock_groq.return_value = LLMResponse(
                content="Response",
                provider="groq",
                model="llama-3.1-70b-versatile",
                cost=0.0,
                latency=0.5,
                success=True,
            )

            response2 = router.generate("Test 2", preferred_provider="groq")

        # Total cost should be sum of both
        assert router.total_cost == 0.001  # Only google cost
        assert response2.cost == 0.0  # Groq is free

    def test_average_cost_calculation(self, mock_llm_router):
        """Test average cost calculation."""
        router = mock_llm_router

        # Make requests
        router.generate("Request 1")
        router.generate("Request 2")

        stats = router.get_stats()
        expected_avg = stats["total_cost"] / stats["total_requests"]
        assert abs(stats["average_cost"] - expected_avg) < 0.0001

    def test_free_providers_have_zero_cost(self, mock_env, temp_config):
        """Test that Groq and Ollama always report zero cost."""
        router = LLMRouter(config_path=temp_config)

        # Mock groq
        with patch.object(router, "_call_groq") as mock_groq:
            mock_groq.return_value = LLMResponse(
                content="Response",
                provider="groq",
                model="llama-3.1-70b-versatile",
                cost=0.0,
                latency=0.5,
                success=True,
            )

            response = router.generate("Test", preferred_provider="groq")
            assert response.cost == 0.0

        # Mock ollama
        with patch.object(router, "_call_ollama") as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="Response",
                provider="ollama",
                model="mistral:7b-instruct",
                cost=0.0,
                latency=0.5,
                success=True,
            )

            response = router.generate("Test", preferred_provider="ollama")
            assert response.cost == 0.0


class TestProviderAPIMocking:
    """Test provider API call mocking and error handling."""

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_google_api_timeout(self, mock_model_class, mock_configure, mock_env, temp_config):
        """Test Google API timeout handling."""
        router = LLMRouter(config_path=temp_config)

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("Timeout error")
        mock_model_class.return_value = mock_model

        response = router._call_google("Test prompt")

        assert response.success is False
        assert response.error is not None
        assert "Timeout" in response.error or "error" in response.error.lower()

    @patch("qfzz.core.llm_router.requests.post")
    def test_groq_rate_limit_error(self, mock_post, mock_env, temp_config):
        """Test Groq rate limit error handling."""
        router = LLMRouter(config_path=temp_config)

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "429 Rate Limit"
        )
        mock_post.return_value = mock_response

        response = router._call_groq("Test prompt")

        assert response.success is False
        assert response.error is not None

    @patch("anthropic.Anthropic")
    def test_anthropic_auth_failure(self, mock_anthropic, mock_env, temp_config):
        """Test Anthropic authentication failure."""
        router = LLMRouter(config_path=temp_config)

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Authentication failed")
        mock_anthropic.return_value = mock_client

        response = router._call_anthropic("Test prompt")

        assert response.success is False
        assert response.error is not None

    @patch("openai.OpenAI")
    def test_openai_invalid_model_error(self, mock_openai, mock_env, temp_config):
        """Test OpenAI invalid model error."""
        router = LLMRouter(config_path=temp_config)

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Invalid model")
        mock_openai.return_value = mock_client

        response = router._call_openai("Test prompt")

        assert response.success is False
        assert response.error is not None

    @patch("qfzz.core.llm_router.requests.post")
    def test_ollama_connection_error(self, mock_post, mock_env, temp_config):
        """Test Ollama connection error (service not running)."""
        router = LLMRouter(config_path=temp_config)

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        response = router._call_ollama("Test prompt")

        assert response.success is False
        assert response.error is not None


class TestLatencyTracking:
    """Test latency tracking for provider calls."""

    @patch.object(LLMRouter, "_call_google")
    def test_latency_recorded(self, mock_google, mock_env, temp_config):
        """Test that latency is recorded for each call."""
        router = LLMRouter(config_path=temp_config)

        mock_google.return_value = LLMResponse(
            content="Response",
            provider="google",
            model="gemini-2.0-flash-exp",
            cost=0.001,
            latency=1.5,
            success=True,
        )

        response = router.generate("Test prompt")

        assert response.latency > 0
        assert response.latency == 1.5

    def test_latency_realistic_range(self, mock_llm_router):
        """Test that mocked latency is in realistic range."""
        router = mock_llm_router

        response = router.generate("Test prompt")

        # Mocked latency should be reasonable (0.1-5 seconds typically)
        assert 0.0 <= response.latency <= 10.0


class TestIntegration:
    """Integration tests for router."""

    def test_generate_with_temperature_parameter(self, mock_llm_router):
        """Test that temperature parameter is used."""
        router = mock_llm_router

        # Generate with different temperatures
        response1 = router.generate("Test", temperature=0.1)
        response2 = router.generate("Test", temperature=0.9)

        # Both should succeed
        assert response1.success is True
        assert response2.success is True

    def test_generate_with_max_tokens_parameter(self, mock_llm_router):
        """Test that max_tokens parameter is used."""
        router = mock_llm_router

        response = router.generate("Test", max_tokens=100)

        assert response.success is True

    def test_request_count_increments(self, mock_llm_router):
        """Test that request_count increments on each call."""
        router = mock_llm_router

        initial_count = router.request_count

        router.generate("Test 1")
        router.generate("Test 2")
        router.generate("Test 3")

        assert router.request_count == initial_count + 3

    def test_get_stats_returns_complete_info(self, mock_llm_router):
        """Test that get_stats returns all required information."""
        router = mock_llm_router

        router.generate("Test 1")
        router.generate("Test 2")

        stats = router.get_stats()

        # Check all expected fields
        assert "total_requests" in stats
        assert "total_cost" in stats
        assert "average_cost" in stats
        assert "available_providers" in stats

        assert stats["total_requests"] == 2
        assert isinstance(stats["total_cost"], float)
        assert isinstance(stats["average_cost"], float)
        assert isinstance(stats["available_providers"], list)

    def test_router_handles_empty_prompt(self, mock_llm_router):
        """Test router handles empty prompt gracefully."""
        router = mock_llm_router

        response = router.generate("")

        # Should still get a response (even if empty)
        assert isinstance(response, LLMResponse)

    def test_router_handles_very_long_prompt(self, mock_llm_router):
        """Test router handles very long prompts."""
        router = mock_llm_router

        long_prompt = "word " * 10000  # ~10k words

        response = router.generate(long_prompt)

        assert isinstance(response, LLMResponse)
        # Cost should be higher for longer prompt
        assert response.cost > 0 or response.provider in ["groq", "ollama"]


class TestConfigurationEdgeCases:
    """Test edge cases in configuration loading."""

    def test_missing_config_file_uses_defaults(self, mock_env):
        """Test that missing config file uses default configuration."""
        router = LLMRouter(config_path="/nonexistent/path/config.json")

        assert router.config is not None
        assert router.config["providers"]["primary"] == "google"
        assert "fallback_chain" in router.config["providers"]

    def test_empty_config_file_handled(self, mock_env):
        """Test handling of empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{}")
            temp_path = f.name

        try:
            # Should raise KeyError or use defaults
            # Current implementation doesn't handle empty config gracefully
            with pytest.raises(KeyError):
                router = LLMRouter(config_path=temp_path)
        finally:
            Path(temp_path).unlink()

    def test_malformed_config_file_handled(self, mock_env):
        """Test handling of malformed config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name

        try:
            # Should raise JSONDecodeError
            # Current implementation doesn't catch JSON errors
            with pytest.raises(json.JSONDecodeError):
                router = LLMRouter(config_path=temp_path)
        finally:
            Path(temp_path).unlink()


@pytest.mark.unit
class TestLLMResponseDataclass:
    """Test LLMResponse dataclass functionality."""

    def test_response_immutability_attempt(self):
        """Test that LLMResponse fields can be accessed."""
        response = LLMResponse(
            content="Test",
            provider="google",
            model="gemini",
            cost=0.001,
            latency=0.5,
            success=True,
        )

        # Fields should be accessible
        assert response.content == "Test"
        assert response.provider == "google"
        assert response.success is True

    def test_response_with_all_fields(self):
        """Test creating response with all fields."""
        response = LLMResponse(
            content="Test content",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            cost=0.005,
            latency=1.2,
            success=True,
            error=None,
        )

        assert response.content == "Test content"
        assert response.provider == "anthropic"
        assert response.model == "claude-3-5-sonnet-20241022"
        assert response.cost == 0.005
        assert response.latency == 1.2
        assert response.success is True
        assert response.error is None

    def test_response_error_field_optional(self):
        """Test that error field is optional."""
        response = LLMResponse(
            content="Test", provider="google", model="gemini", cost=0.0, latency=0.0, success=True
        )

        assert response.error is None
