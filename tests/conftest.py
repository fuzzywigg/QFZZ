"""
Shared fixtures and configuration for QFZZ tests.

Provides reusable fixtures for state management, LLM routing, and test utilities.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from qfzz.core.llm_router import LLMResponse, LLMRouter
from qfzz.core.state import StateManager


# ============================================================================
# Honeycomb State Fixtures
# ============================================================================


@pytest.fixture
def temp_honeycomb():
    """Create temporary honeycomb directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def state_manager(temp_honeycomb):
    """Create StateManager with temporary directory."""
    return StateManager(honeycomb_dir=temp_honeycomb)


# ============================================================================
# LLM Router Fixtures
# ============================================================================


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for LLM providers."""
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "test_google_key")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    # Ollama doesn't require API key
    return {
        "google": "test_google_key",
        "groq": "test_groq_key",
        "anthropic": "test_anthropic_key",
        "openai": "test_openai_key",
    }


@pytest.fixture
def temp_config():
    """Create temporary config file for LLM router testing."""
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
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_llm_router(mock_env, temp_config):
    """Create LLM router with mocked providers."""
    router = LLMRouter(config_path=temp_config)

    # Mock all provider methods to return predictable responses
    def create_mock_response(provider, model, cost_per_1k):
        def mock_call(prompt, temperature=0.7, max_tokens=1000):
            # Simulate token counting (rough estimate)
            prompt_tokens = len(prompt.split()) * 1.3  # Rough token count
            response_tokens = 100  # Fixed response size for testing
            total_tokens = prompt_tokens + response_tokens
            cost = (total_tokens / 1000) * cost_per_1k

            return LLMResponse(
                content=f"Mock response from {provider}",
                provider=provider,
                model=model,
                cost=cost,
                latency=0.5,
                success=True,
            )

        return mock_call

    # Apply mocks
    router._call_google = create_mock_response("google", "gemini-2.0-flash-exp", 0.000075)
    router._call_groq = create_mock_response("groq", "llama-3.1-70b-versatile", 0.0)
    router._call_anthropic = create_mock_response("anthropic", "claude-3-5-sonnet-20241022", 0.003)
    router._call_openai = create_mock_response("openai", "gpt-4o-mini", 0.00015)
    router._call_ollama = create_mock_response("ollama", "mistral:7b-instruct", 0.0)

    return router


# ============================================================================
# Environment and Configuration Fixtures
# ============================================================================


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all QFZZ-related environment variables."""
    env_vars_to_remove = [
        "GOOGLE_AI_API_KEY",
        "GROQ_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "OLLAMA_BASE_URL",
    ]

    for var in env_vars_to_remove:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def temp_dotenv():
    """Create temporary .env file for testing."""
    env_content = """
# Test environment variables
GOOGLE_AI_API_KEY=test_google_secret_123
GROQ_API_KEY=test_groq_secret_456
ANTHROPIC_API_KEY=test_anthropic_secret_789
OPENAI_API_KEY=test_openai_secret_abc
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(env_content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_api: mark test as requiring external API")


# ============================================================================
# Test Utilities
# ============================================================================


@pytest.fixture
def mock_file_corruption(monkeypatch):
    """Mock file corruption for testing error recovery."""

    def corrupt_json_file(filepath):
        """Write corrupted JSON to file."""
        with open(filepath, "w") as f:
            f.write("{invalid json content")

    return corrupt_json_file


@pytest.fixture
def assert_no_secrets_in_output():
    """Fixture to verify no secrets leak in output."""

    def checker(output: str, secrets: list[str]):
        """Check that none of the secrets appear in output."""
        for secret in secrets:
            assert secret not in output, f"Secret '{secret}' found in output!"

    return checker
