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
        "cohere": {
            "name": "Cohere",
            "base_url": "https://api.cohere.com/v1",
            "models": ["command-r-plus", "command-r"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/chat",
        },
        "ollama": {
            "name": "Ollama (Local)",
            "base_url": "http://localhost:11434/v1",
            "models": ["llama3", "phi4-mini", "qwen3:0.6b"],
            "headers": lambda key: {"Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
        "huggingface": {
            "name": "Hugging Face",
            "base_url": "https://api-inference.huggingface.co/models",
            "models": ["mistralai/Mistral-7B-Instruct-v0.2", "meta-llama/Llama-2-70b-chat-hf"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/{model}",
        },
        "openrouter": {
            "name": "OpenRouter",
            "base_url": "https://openrouter.ai/api/v1",
            "models": ["meta-llama/llama-3.1-70b-instruct:free", "anthropic/claude-3.5-sonnet"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "HTTP-Referer": "https://ai-startup.app", "X-Title": "AI Startup"},
            "chat_endpoint": "/chat/completions",
        },
        "xai": {
            "name": "xAI (Grok)",
            "base_url": "https://api.x.ai/v1",
            "models": ["grok-beta", "grok-vision-beta"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
        "kimi": {
            "name": "KIMI (Moonshot)",
            "base_url": "https://api.moonshot.cn/v1",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "chat_endpoint": "/chat/completions",
        },
    }

    def __init__(self):
        self.settings = get_settings()
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._active_provider: Optional[str] = None
        self._provider_settings: Dict[str, dict] = {}
        self._metrics = {
            "requests": 0,
            "errors": 0,
            "provider_usage": {},
        }

    async def _load_provider_settings(self):
        """Load provider settings from settings_api memory."""
        try:
            from app.routers.settings_api import _providers_memory
            self._provider_settings = {
                pid: {
                    "api_key": p.get("api_key", ""),
                    "base_url": p.get("base_url", ""),
                    "default_model": p.get("default_model", ""),
                    "is_active": p.get("is_active", False),
                    "temperature": p.get("temperature", 0.7),
                    "max_tokens": p.get("max_tokens", 2048),
                }
                for pid, p in _providers_memory.items()
            }
        except Exception as e:
            logger.warning(f"Could not load provider settings: {e}")
            self._provider_settings = {}

    def _get_api_key(self, provider_id: str) -> Optional[str]:
        """Get API key for a provider from settings or environment."""
        if provider_id in self._provider_settings:
            key = self._provider_settings[provider_id].get("api_key", "")
            if key and key != "local":
                return key

        env_vars = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "cohere": "COHERE_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "huggingface": "HF_API_KEY",
            "xai": "XAI_API_KEY",
            "kimi": "KIMI_API_KEY",
            "ollama": None,
        }
        env_var = env_vars.get(provider_id)
        if env_var:
            key = os.getenv(env_var, "")
            if key:
                return key
        return "local" if provider_id == "ollama" else None

    def _get_base_url(self, provider_id: str) -> str:
        """Get base URL for a provider."""
        if provider_id in self._provider_settings:
            url = self._provider_settings[provider_id].get("base_url", "")
            if url:
                return url
        return self.PROVIDERS.get(provider_id, {}).get("base_url", "")

    def _get_model(self, provider_id: str) -> str:
        """Get default model for a provider."""
        if provider_id in self._provider_settings:
            model = self._provider_settings[provider_id].get("default_model", "")
            if model:
                return model
        return self.PROVIDERS.get(provider_id, {}).get("models", [""])[0]

    async def _get_active_provider(self) -> Optional[str]:
        """Determine which provider to use based on settings."""
        await self._load_provider_settings()

        for provider_id, settings in self._provider_settings.items():
            if settings.get("is_active") and settings.get("api_key"):
                self._active_provider = provider_id
                return provider_id

        for provider_id in self.PROVIDERS.keys():
            api_key = self._get_api_key(provider_id)
            if api_key and api_key != "local" and api_key != "":
                self._active_provider = provider_id
                return provider_id

        return "ollama"

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

        provider_id = await self._get_active_provider()

        if not provider_id:
            return {
                "success": False,
                "error": "No AI provider available. Please configure an API key in Settings.",
                "setup_url": "/settings",
            }

        api_key = self._get_api_key(provider_id)
        if not api_key and provider_id != "ollama":
            return {
                "success": False,
                "error": f"{provider_id} API key not configured. Please add it in Settings.",
                "setup_url": "/settings",
            }

        try:
            base_url = self._get_base_url(provider_id)
            config = self.PROVIDERS[provider_id]

            client = httpx.AsyncClient(
                base_url=base_url,
                headers=config["headers"](api_key or ""),
                timeout=120.0,
            )

            if provider_id == "anthropic":
                payload = {
                    "model": model or self._get_model(provider_id),
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            elif provider_id == "google":
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
            elif provider_id == "cohere":
                payload = {
                    "model": model or self._get_model(provider_id),
                    "message": messages[-1]["content"] if messages else "",
                    "chat_history": [{"role": m["role"], "message": m["content"]} for m in messages[:-1]],
                    "temperature": temperature,
                }
            else:
                payload = {
                    "model": model or self._get_model(provider_id),
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream,
                }

            if provider_id == "google":
                endpoint = config["chat_endpoint"].format(
                    model=model or self._get_model(provider_id), 
                    key=api_key
                )
                response = await client.post(endpoint, json=payload)
            else:
                response = await client.post(config["chat_endpoint"], json=payload)

            response.raise_for_status()
            data = response.json()

            if provider_id == "google":
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            elif provider_id == "anthropic":
                content = data.get("content", [{}])[0].get("text", "")
                usage = data.get("usage", {})
            elif provider_id == "cohere":
                content = data.get("text", "")
                usage = data.get("meta", {}).get("billed_units", {})
            else:
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})

            self._metrics["requests"] += 1
            self._metrics["provider_usage"][provider_id] = self._metrics["provider_usage"].get(provider_id, 0) + 1

            return {
                "success": True,
                "content": content,
                "model": model or self._get_model(provider_id),
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

    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            "total_requests": self._metrics["requests"],
            "total_errors": self._metrics["errors"],
            "provider_usage": self._metrics["provider_usage"],
            "active_provider": self._active_provider,
        }


_multi_provider_service: Optional[MultiProviderAIService] = None

async def get_multi_provider_service() -> MultiProviderAIService:
    """Get or create multi-provider service."""
    global _multi_provider_service
    if _multi_provider_service is None:
        _multi_provider_service = MultiProviderAIService()
    return _multi_provider_service
