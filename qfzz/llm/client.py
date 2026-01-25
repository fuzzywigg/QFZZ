"""
LLM Client implementations for QFZZ.
Supports local Ollama instances and generic text generation.
"""

import json
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from a prompt."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class MockLLMClient(LLMProvider):
    """Fallback LLM that returns static responses."""
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"I'm a placeholder DJ. I heard you say: '{prompt}'. (Connect a real LLM to hear more!)"
        
    def is_available(self) -> bool:
        return True


class OllamaClient(LLMProvider):
    """Client for local Ollama instance."""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._available = False
        self._check_availability()
        
    def _check_availability(self):
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=1) as response:
                if response.status == 200:
                    self._available = True
                    logger.info(f"Ollama connected at {self.base_url}")
        except Exception:
            self._available = False
            logger.warning(f"Ollama not found at {self.base_url}")

    def is_available(self) -> bool:
        return self._available

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._available:
            return "Ollama is not connected."
            
        url = f"{self.base_url}/api/generate"
        
        # Simple non-streaming request
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "system": system_prompt or "You are a helpful AI DJ for QFZZ radio station."
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return f"Error generating response: {e}"


class GeminiClient(LLMProvider):
    """Client for Google's Gemini API (Free Tier)."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model
        self._available = False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self._available = True
            logger.info(f"Gemini API configured with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._available:
            return "Gemini API is not available."
            
        try:
            # Combine system prompt with user prompt since regular generate_content
            # doesn't always support system instructions purely in 1.0 versions cleanly
            # or keep it simple for now. 1.5 supports system instructions better during model init
            # but for 100% compatibility, we can just prepend.
            full_prompt = prompt
            if system_prompt:
                # Re-configure model with system prompt if possible, or just prepend
                # For this simple client, prepending is safer and universally working
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return f"Error generating response: {e}"
