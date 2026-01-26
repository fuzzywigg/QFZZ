"""
QFZZ LLM Router

Multi-provider LLM router with automatic fallback and cost optimization.
Supports Google Gemini, Groq, Anthropic Claude, OpenAI, and local Ollama.
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    provider: str
    model: str
    cost: float
    latency: float
    success: bool
    error: Optional[str] = None


class LLMRouter:
    """
    Routes LLM requests through multiple providers with automatic fallback.
    
    Supports cost optimization and provider-specific parameters.
    """

    def __init__(self, config_path: str = "config/llm-router-config.json"):
        """
        Initialize LLM Router.
        
        Args:
            config_path: Path to router configuration file
        """
        self.config = self._load_config(config_path)
        self.providers = self._initialize_providers()
        self.request_count = 0
        self.total_cost = 0.0

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load router configuration."""
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "providers": {
                "primary": "google",
                "fallback_chain": ["groq", "anthropic", "openai", "ollama"],
                "cost_optimization": {
                    "prefer_cheap": True,
                    "max_cost_per_request": 0.01
                }
            },
            "models": {
                "google": os.getenv("GOOGLE_AI_MODEL_DEFAULT", "gemini-2.0-flash-exp"),
                "anthropic": os.getenv("CLAUDE_MODEL_DEFAULT", "claude-3-5-sonnet-20241022"),
                "openai": os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini"),
                "groq": "llama-3.1-70b-versatile",
                "ollama": os.getenv("OLLAMA_MODEL_DEFAULT", "mistral:7b-instruct")
            }
        }

    def _initialize_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize provider configurations."""
        return {
            "google": {
                "api_key": os.getenv("GOOGLE_AI_API_KEY"),
                "model": self.config["models"]["google"],
                "cost_per_1k": 0.000075,  # Approximate for Gemini Flash
                "available": bool(os.getenv("GOOGLE_AI_API_KEY"))
            },
            "groq": {
                "api_key": os.getenv("GROQ_API_KEY"),
                "model": self.config["models"]["groq"],
                "cost_per_1k": 0.0,  # Free tier
                "available": bool(os.getenv("GROQ_API_KEY"))
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": self.config["models"]["anthropic"],
                "cost_per_1k": 0.003,  # Approximate for Claude Sonnet
                "available": bool(os.getenv("ANTHROPIC_API_KEY"))
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": self.config["models"]["openai"],
                "cost_per_1k": 0.00015,  # Approximate for GPT-4o-mini
                "available": bool(os.getenv("OPENAI_API_KEY"))
            },
            "ollama": {
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": self.config["models"]["ollama"],
                "cost_per_1k": 0.0,  # Local, no cost
                "available": True  # Always available (fallback)
            }
        }

    def _call_google(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """Call Google Gemini API."""
        try:
            import google.generativeai as genai
            
            provider_config = self.providers["google"]
            genai.configure(api_key=provider_config["api_key"])
            
            model = genai.GenerativeModel(provider_config["model"])
            
            start_time = time.time()
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            latency = time.time() - start_time
            
            content = response.text
            cost = (len(prompt) + len(content)) / 1000 * provider_config["cost_per_1k"]
            
            return LLMResponse(
                content=content,
                provider="google",
                model=provider_config["model"],
                cost=cost,
                latency=latency,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                provider="google",
                model=self.providers["google"]["model"],
                cost=0.0,
                latency=0.0,
                success=False,
                error=str(e)
            )

    def _call_groq(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """Call Groq API."""
        try:
            provider_config = self.providers["groq"]
            
            headers = {
                "Authorization": f"Bearer {provider_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": provider_config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            start_time = time.time()
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            latency = time.time() - start_time
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            cost = 0.0  # Groq is free tier
            
            return LLMResponse(
                content=content,
                provider="groq",
                model=provider_config["model"],
                cost=cost,
                latency=latency,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                provider="groq",
                model=self.providers["groq"]["model"],
                cost=0.0,
                latency=0.0,
                success=False,
                error=str(e)
            )

    def _call_anthropic(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """Call Anthropic Claude API."""
        try:
            from anthropic import Anthropic
            
            provider_config = self.providers["anthropic"]
            client = Anthropic(api_key=provider_config["api_key"])
            
            start_time = time.time()
            response = client.messages.create(
                model=provider_config["model"],
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            latency = time.time() - start_time
            
            content = response.content[0].text
            cost = (len(prompt) + len(content)) / 1000 * provider_config["cost_per_1k"]
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=provider_config["model"],
                cost=cost,
                latency=latency,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.providers["anthropic"]["model"],
                cost=0.0,
                latency=0.0,
                success=False,
                error=str(e)
            )

    def _call_openai(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """Call OpenAI API."""
        try:
            from openai import OpenAI
            
            provider_config = self.providers["openai"]
            client = OpenAI(api_key=provider_config["api_key"])
            
            start_time = time.time()
            response = client.chat.completions.create(
                model=provider_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            latency = time.time() - start_time
            
            content = response.choices[0].message.content
            cost = (len(prompt) + len(content)) / 1000 * provider_config["cost_per_1k"]
            
            return LLMResponse(
                content=content,
                provider="openai",
                model=provider_config["model"],
                cost=cost,
                latency=latency,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                provider="openai",
                model=self.providers["openai"]["model"],
                cost=0.0,
                latency=0.0,
                success=False,
                error=str(e)
            )

    def _call_ollama(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """Call local Ollama API."""
        try:
            provider_config = self.providers["ollama"]
            
            data = {
                "model": provider_config["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{provider_config['base_url']}/api/generate",
                json=data,
                timeout=60
            )
            latency = time.time() - start_time
            
            response.raise_for_status()
            result = response.json()
            
            content = result["response"]
            
            return LLMResponse(
                content=content,
                provider="ollama",
                model=provider_config["model"],
                cost=0.0,
                latency=latency,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                provider="ollama",
                model=self.providers["ollama"]["model"],
                cost=0.0,
                latency=0.0,
                success=False,
                error=str(e)
            )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        preferred_provider: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate response using LLM with automatic fallback.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            preferred_provider: Optional preferred provider override
            
        Returns:
            LLMResponse with generated content
        """
        self.request_count += 1
        
        # Build provider chain
        if preferred_provider and self.providers.get(preferred_provider, {}).get("available"):
            chain = [preferred_provider]
        else:
            chain = [self.config["providers"]["primary"]]
        
        # Add fallback chain
        for provider in self.config["providers"]["fallback_chain"]:
            if provider not in chain and self.providers.get(provider, {}).get("available"):
                chain.append(provider)
        
        # Try each provider in chain
        last_error = None
        for provider in chain:
            try:
                # Call provider
                if provider == "google":
                    response = self._call_google(prompt, temperature, max_tokens)
                elif provider == "groq":
                    response = self._call_groq(prompt, temperature, max_tokens)
                elif provider == "anthropic":
                    response = self._call_anthropic(prompt, temperature, max_tokens)
                elif provider == "openai":
                    response = self._call_openai(prompt, temperature, max_tokens)
                elif provider == "ollama":
                    response = self._call_ollama(prompt, temperature, max_tokens)
                else:
                    continue
                
                if response.success:
                    self.total_cost += response.cost
                    return response
                
                last_error = response.error
                
            except Exception as e:
                last_error = str(e)
                continue
        
        # All providers failed
        return LLMResponse(
            content="",
            provider="none",
            model="",
            cost=0.0,
            latency=0.0,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            "total_requests": self.request_count,
            "total_cost": self.total_cost,
            "average_cost": self.total_cost / self.request_count if self.request_count > 0 else 0,
            "available_providers": [
                name for name, config in self.providers.items()
                if config.get("available", False)
            ]
        }
