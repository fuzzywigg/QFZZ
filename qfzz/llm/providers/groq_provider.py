"""
Groq LLM Provider for QFZZ.
Provides free-tier access to fast inference.
"""

import json
import logging
import urllib.error
import urllib.request
from typing import Optional

from qfzz.exceptions import LLMAuthenticationError, LLMConnectionError, LLMGenerationError

logger = logging.getLogger(__name__)


class GroqProvider:
    """Client for Groq API (free tier available)."""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        self._available = bool(api_key)

        if self._available:
            logger.info(f"Groq provider initialized with model: {model}")

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self._available and self.api_key is not None

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 500
    ) -> str:
        """
        Generate text using Groq API.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            LLMConnectionError: If connection fails
            LLMGenerationError: If generation fails
            LLMAuthenticationError: If authentication fails
        """
        if not self.is_available():
            raise LLMConnectionError("Groq provider is not available (missing API key)")

        url = f"{self.base_url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            req = urllib.request.Request(url, data=data, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise LLMAuthenticationError(
                    f"Groq authentication failed: {e}", {"status_code": e.code}
                )
            elif e.code == 429:
                raise LLMGenerationError(f"Groq rate limit exceeded: {e}", {"status_code": e.code})
            else:
                raise LLMGenerationError(f"Groq API error: {e}", {"status_code": e.code})
        except urllib.error.URLError as e:
            raise LLMConnectionError(f"Failed to connect to Groq: {e}")
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise LLMGenerationError(f"Groq generation error: {e}")
