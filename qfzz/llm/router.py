"""
LLM Router for QFZZ.
Manages multiple LLM providers with automatic fallback and health checks.
"""

import logging
import time
from typing import Optional, List, Dict, Any
from qfzz.llm.client import OllamaClient, GeminiClient, MockLLMClient
from qfzz.llm.providers.groq_provider import GroqProvider
from qfzz.llm.providers.together_provider import TogetherProvider
from qfzz.llm.providers.huggingface_provider import HuggingFaceProvider
from qfzz.exceptions import LLMProviderError, LLMConnectionError
from qfzz.config.settings import get_config

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Routes LLM requests to available providers with automatic fallback.
    
    Priority order:
    1. Ollama (local, free, privacy-preserving)
    2. Groq (free tier API)
    3. Together.ai (free tier)
    4. HuggingFace Inference API (free tier)
    5. Gemini (optional paid/free tier)
    6. Mock (always available fallback)
    """
    
    def __init__(self, config=None):
        """
        Initialize LLM router.
        
        Args:
            config: Optional configuration settings (uses global config if None)
        """
        self.config = config or get_config()
        self.providers: List[Dict[str, Any]] = []
        self._initialize_providers()
        self._health_check_cache: Dict[str, Dict[str, Any]] = {}
        self._health_check_ttl = 60  # Cache health checks for 60 seconds
    
    def _initialize_providers(self):
        """Initialize all available LLM providers in priority order."""
        llm_config = self.config.llm
        
        # 1. Ollama (local)
        try:
            ollama = OllamaClient(
                model=llm_config.ollama_model,
                base_url=llm_config.ollama_base_url
            )
            self.providers.append({
                'name': 'Ollama',
                'provider': ollama,
                'priority': 1,
                'type': 'local'
            })
            if ollama.is_available():
                logger.info("Ollama provider initialized and available")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {e}")
        
        # 2. Groq
        if llm_config.groq_api_key:
            try:
                groq = GroqProvider(api_key=llm_config.groq_api_key)
                self.providers.append({
                    'name': 'Groq',
                    'provider': groq,
                    'priority': 2,
                    'type': 'api'
                })
                logger.info("Groq provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
        
        # 3. Together.ai
        if llm_config.together_api_key:
            try:
                together = TogetherProvider(api_key=llm_config.together_api_key)
                self.providers.append({
                    'name': 'Together.ai',
                    'provider': together,
                    'priority': 3,
                    'type': 'api'
                })
                logger.info("Together.ai provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Together.ai: {e}")
        
        # 4. HuggingFace
        if llm_config.huggingface_api_key:
            try:
                hf = HuggingFaceProvider(api_key=llm_config.huggingface_api_key)
                self.providers.append({
                    'name': 'HuggingFace',
                    'provider': hf,
                    'priority': 4,
                    'type': 'api'
                })
                logger.info("HuggingFace provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace: {e}")
        
        # 5. Gemini (optional)
        if llm_config.gemini_api_key:
            try:
                gemini = GeminiClient(api_key=llm_config.gemini_api_key)
                self.providers.append({
                    'name': 'Gemini',
                    'provider': gemini,
                    'priority': 5,
                    'type': 'api'
                })
                if gemini.is_available():
                    logger.info("Gemini provider initialized and available")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        
        # 6. Mock (always available fallback)
        mock = MockLLMClient()
        self.providers.append({
            'name': 'Mock',
            'provider': mock,
            'priority': 99,
            'type': 'fallback'
        })
        logger.info("Mock provider initialized as fallback")
        
        # Sort by priority
        self.providers.sort(key=lambda x: x['priority'])
        
        logger.info(f"LLM Router initialized with {len(self.providers)} providers")
    
    def _is_provider_healthy(self, provider_info: Dict[str, Any]) -> bool:
        """
        Check if a provider is healthy.
        
        Args:
            provider_info: Provider information dictionary
            
        Returns:
            True if provider is healthy, False otherwise
        """
        provider_name = provider_info['name']
        
        # Check cache
        if provider_name in self._health_check_cache:
            cache_entry = self._health_check_cache[provider_name]
            if time.time() - cache_entry['timestamp'] < self._health_check_ttl:
                return cache_entry['healthy']
        
        # Perform health check
        try:
            provider = provider_info['provider']
            healthy = provider.is_available()
            
            # Cache result
            self._health_check_cache[provider_name] = {
                'healthy': healthy,
                'timestamp': time.time()
            }
            
            return healthy
        except Exception as e:
            logger.debug(f"Health check failed for {provider_name}: {e}")
            self._health_check_cache[provider_name] = {
                'healthy': False,
                'timestamp': time.time()
            }
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate text using the first available provider.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with 'text' and 'provider' keys
        """
        last_error = None
        
        for provider_info in self.providers:
            provider_name = provider_info['name']
            provider = provider_info['provider']
            
            # Skip unhealthy providers (except fallback)
            if provider_info['type'] != 'fallback' and not self._is_provider_healthy(provider_info):
                logger.debug(f"Skipping unhealthy provider: {provider_name}")
                continue
            
            try:
                logger.debug(f"Attempting generation with {provider_name}")
                
                # Try to generate
                if hasattr(provider, 'generate'):
                    text = provider.generate(prompt, system_prompt, max_tokens)
                else:
                    text = provider.generate(prompt, system_prompt)
                
                logger.info(f"Successfully generated response using {provider_name}")
                return {
                    'text': text,
                    'provider': provider_name,
                    'success': True
                }
                
            except LLMProviderError as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue
            except Exception as e:
                logger.warning(f"Unexpected error with {provider_name}: {e}")
                last_error = e
                continue
        
        # If we get here, all providers failed
        error_msg = f"All LLM providers failed. Last error: {last_error}"
        logger.error(error_msg)
        return {
            'text': f"[All LLM providers unavailable] {error_msg}",
            'provider': 'None',
            'success': False,
            'error': str(last_error)
        }
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of currently available provider names.
        
        Returns:
            List of provider names
        """
        available = []
        for provider_info in self.providers:
            if self._is_provider_healthy(provider_info):
                available.append(provider_info['name'])
        return available
    
    def clear_health_cache(self):
        """Clear health check cache to force re-checking."""
        self._health_check_cache.clear()
        logger.debug("Health check cache cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all providers.
        
        Returns:
            Dictionary with provider status information
        """
        status = {
            'total_providers': len(self.providers),
            'available_providers': [],
            'unavailable_providers': [],
            'providers': []
        }
        
        for provider_info in self.providers:
            provider_name = provider_info['name']
            healthy = self._is_provider_healthy(provider_info)
            
            provider_status = {
                'name': provider_name,
                'priority': provider_info['priority'],
                'type': provider_info['type'],
                'healthy': healthy
            }
            
            status['providers'].append(provider_status)
            
            if healthy:
                status['available_providers'].append(provider_name)
            else:
                status['unavailable_providers'].append(provider_name)
        
        return status
