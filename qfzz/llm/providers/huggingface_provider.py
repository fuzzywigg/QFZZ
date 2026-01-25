"""
HuggingFace Inference API Provider for QFZZ.
Provides free-tier access to models hosted on HuggingFace.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional
from qfzz.exceptions import LLMConnectionError, LLMGenerationError, LLMAuthenticationError

logger = logging.getLogger(__name__)


class HuggingFaceProvider:
    """Client for HuggingFace Inference API (free tier available)."""
    
    def __init__(self, api_key: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"):
        """
        Initialize HuggingFace provider.
        
        Args:
            api_key: HuggingFace API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api-inference.huggingface.co/models"
        self._available = bool(api_key)
        
        if self._available:
            logger.info(f"HuggingFace provider initialized with model: {model}")
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        return self._available and self.api_key is not None
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 500) -> str:
        """
        Generate text using HuggingFace Inference API.
        
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
            raise LLMConnectionError("HuggingFace provider is not available (missing API key)")
        
        url = f"{self.base_url}/{self.model}"
        
        # Combine system and user prompts
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"[INST] {system_prompt}\n\n{prompt} [/INST]"
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            req = urllib.request.Request(url, data=data, headers=headers)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', '')
                else:
                    raise LLMGenerationError("Unexpected response format from HuggingFace")
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise LLMAuthenticationError(f"HuggingFace authentication failed: {e}", {"status_code": e.code})
            elif e.code == 429:
                raise LLMGenerationError(f"HuggingFace rate limit exceeded: {e}", {"status_code": e.code})
            elif e.code == 503:
                raise LLMGenerationError(f"HuggingFace model is loading, try again later: {e}", {"status_code": e.code})
            else:
                raise LLMGenerationError(f"HuggingFace API error: {e}", {"status_code": e.code})
        except urllib.error.URLError as e:
            raise LLMConnectionError(f"Failed to connect to HuggingFace: {e}")
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            raise LLMGenerationError(f"HuggingFace generation error: {e}")
