"""Multi-Provider AI Service - Supports Groq, OpenAI, Google Gemini, Anthropic, etc.

Automatically selects the best available provider based on configuration.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class MultiProviderAIService:
    """Multi-provider AI service supporting Groq, OpenAI, Gemini, Claude, etc."""

    # Provider configurations
    # Free API keys for demo/testing (rate limited)
    DEFAULT_KEYS = {
        "openrouter": "sk-or-v1-demo",  # Users should replace with their own
    }

    PROVIDERS = {
        "groq": {
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
        "openai": {
            "name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
        "google": {
            "name": "Google Gemini",
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
            "headers": lambda key: {"Content-Type": "application/json"},
            "chat_endpoint": "/models/{model}:generateContent?key={key}",
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "base_url": "https://api.anthropic.com/v1",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
            "headers": lambda key: {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            "chat_endpoint": "/messages",
        },
        "mistral": {
            "name": "Mistral AI",
            "base_url": "https://api.mistral.ai/v1",
            "models": ["mistral-large-latest", "mistral-medium-latest"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
        "ollama": {
            "name": "Ollama (Local)",
            "base_url": "http://localhost:11434/v1",
            "models": ["llama3", "phi4-mini", "qwen3:0.6b"],
            "headers": lambda key: {"Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
    }

    def __init__(self):
        self.settings = get_settings()
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._active_provider: Optional[str] = None
        self._metrics = {
            "requests": 0,
            "errors": 0,
            "provider_usage": {},
        }

    def _get_client(self, provider_id: str, api_key: str) -> httpx.AsyncClient:
        """Get or create HTTP client for a provider."""
        if provider_id not in self._clients:
            config = self.PROVIDERS.get(provider_id, self.PROVIDERS["groq"])
            self._clients[provider_id] = httpx.AsyncClient(
                base_url=config["base_url"],
                headers=config["headers"](api_key),
                timeout=120.0,
            )
        return self._clients[provider_id]

    def _get_api_key(self, provider_id: str) -> Optional[str]:
        """Get API key for a provider from environment or defaults."""
        env_vars = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "ollama": None,  # Local, no key needed
        }
        env_var = env_vars.get(provider_id)
        if env_var:
            key = os.getenv(env_var, "")
            if key:
                return key
            # Try default keys for demo
            return self.DEFAULT_KEYS.get(provider_id, "")
        return "local" if provider_id == "ollama" else None

    def _get_active_provider(self) -> Optional[str]:
        """Determine which provider to use."""
        if self._active_provider:
            return self._active_provider

        # Priority order - try free/cheap providers first
        for provider_id in ["groq", "openrouter", "openai", "google", "anthropic", "mistral", "ollama"]:
            api_key = self._get_api_key(provider_id)
            if api_key and api_key != "local" and api_key != "":
                self._active_provider = provider_id
                return provider_id
            elif provider_id == "ollama":
                # Check if Ollama is running
                self._active_provider = "ollama"
                return "ollama"

        return None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send chat completion request to active provider."""
        import time
        start_time = time.time()

        provider_id = self._get_active_provider()

        if not provider_id:
            return {
                "success": False,
                "error": "No AI provider available. Please set GROQ_API_KEY in Railway Variables or add a key in Settings page.",
                "providers": list(self.PROVIDERS.keys()),
                "setup_url": "/settings",
            }

        api_key = self._get_api_key(provider_id)
        if not api_key and provider_id != "ollama":
            return {
                "success": False,
                "error": f"{provider_id} API key not configured.",
            }

        try:
            client = self._get_client(provider_id, api_key or "")
            config = self.PROVIDERS[provider_id]

            # Format messages based on provider
            if provider_id == "anthropic":
                payload = {
                    "model": model or config["models"][0],
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            elif provider_id == "google":
                # Convert to Gemini format
                gemini_messages = []
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
                payload = {
                    "contents": gemini_messages,
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                }
            else:
                payload = {
                    "model": model or config["models"][0],
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream,
                }

            # Determine endpoint
            if provider_id == "google":
                endpoint = config["chat_endpoint"].format(model=model or config["models"][0], key=api_key)
                response = await client.post(endpoint, json=payload)
            else:
                response = await client.post(config["chat_endpoint"], json=payload)

            response.raise_for_status()
            data = response.json()

            # Parse response based on provider
            if provider_id == "google":
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            elif provider_id == "anthropic":
                content = data.get("content", [{}])[0].get("text", "")
                usage = data.get("usage", {})
            else:
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})

            self._metrics["requests"] += 1
            self._metrics["provider_usage"][provider_id] = self._metrics["provider_usage"].get(provider_id, 0) + 1

            return {
                "success": True,
                "content": content,
                "model": model or config["models"][0],
                "provider": provider_id,
                "usage": usage,
                "execution_time_ms": (time.time() - start_time) * 1000,
            }

        except httpx.HTTPStatusError as e:
            self._metrics["errors"] += 1
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            if e.response.status_code == 401:
                error_msg = f"Invalid API key for {provider_id}. Please check your settings."
            elif e.response.status_code == 429:
                error_msg = f"Rate limit exceeded for {provider_id}. Please try again later."
            return {
                "success": False,
                "error": error_msg,
                "provider": provider_id,
                "execution_time_ms": (time.time() - start_time) * 1000,
            }
        except Exception as e:
            self._metrics["errors"] += 1
            return {
                "success": False,
                "error": f"{provider_id} error: {str(e)}",
                "provider": provider_id,
                "execution_time_ms": (time.time() - start_time) * 1000,
            }

    async def list_models(self, provider_id: Optional[str] = None) -> List[str]:
        """List available models for a provider."""
        if provider_id:
            config = self.PROVIDERS.get(provider_id)
            return config["models"] if config else []

        # Return models for active provider
        active = self._get_active_provider()
        if active:
            return self.PROVIDERS[active]["models"]
        return []

    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            **self._metrics,
            "active_provider": self._get_active_provider(),
        }

    async def set_active_provider(self, provider_id: str) -> bool:
        """Manually set the active provider."""
        if provider_id in self.PROVIDERS:
            self._active_provider = provider_id
            return True
        return False


# Singleton
_multi_provider_service: Optional[MultiProviderAIService] = None

async def get_multi_provider_service() -> MultiProviderAIService:
    """Get or create the multi-provider service."""
    global _multi_provider_service
    if _multi_provider_service is None:
        _multi_provider_service = MultiProviderAIService()
    return _multi_provider_service
