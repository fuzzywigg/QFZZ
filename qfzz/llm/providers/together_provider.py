"""
Together.ai LLM Provider for QFZZ.
Provides free-tier access to various open-source models.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional
from qfzz.exceptions import LLMConnectionError, LLMGenerationError, LLMAuthenticationError

logger = logging.getLogger(__name__)


class TogetherProvider:
    """Client for Together.ai API (free tier available)."""
    
    def __init__(self, api_key: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"):
        """
        Initialize Together.ai provider.
        
        Args:
            api_key: Together.ai API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.together.xyz"
        self._available = bool(api_key)
        
        if self._available:
            logger.info(f"Together.ai provider initialized with model: {model}")
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        return self._available and self.api_key is not None
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 500) -> str:
        """
        Generate text using Together.ai API.
        
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
            raise LLMConnectionError("Together.ai provider is not available (missing API key)")
        
        url = f"{self.base_url}/v1/chat/completions"
        
        # Combine system and user prompts
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": full_prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            req = urllib.request.Request(url, data=data, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise LLMAuthenticationError(f"Together.ai authentication failed: {e}", {"status_code": e.code})
            elif e.code == 429:
                raise LLMGenerationError(f"Together.ai rate limit exceeded: {e}", {"status_code": e.code})
            else:
                raise LLMGenerationError(f"Together.ai API error: {e}", {"status_code": e.code})
        except urllib.error.URLError as e:
            raise LLMConnectionError(f"Failed to connect to Together.ai: {e}")
        except Exception as e:
            logger.error(f"Together.ai generation failed: {e}")
            raise LLMGenerationError(f"Together.ai generation error: {e}")
