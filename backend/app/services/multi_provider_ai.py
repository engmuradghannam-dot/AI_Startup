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


def _split_content(content: Any) -> tuple:
    """Split an OpenAI-style content value into (text, image_data_url).

    content is either a plain string, or a list of
    [{"type": "text", "text": ...}, {"type": "image_url", "image_url": {"url": "data:..."}}]
    parts as produced by the chat router when an image is attached.
    """
    if isinstance(content, str):
        return content, None

    text = ""
    image_url = None
    for part in content:
        if part.get("type") == "text":
            text = part.get("text", "")
        elif part.get("type") == "image_url":
            image_url = part.get("image_url", {}).get("url")
    return text, image_url


class MultiProviderAIService:
    """Multi-provider AI service supporting Groq, OpenAI, Gemini, Claude, etc."""

    PROVIDERS = {
        "groq": {
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
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
                anthropic_messages = []
                for msg in messages:
                    text, image_url = _split_content(msg["content"])
                    if image_url:
                        media_type, b64_data = image_url.split(";base64,", 1) if ";base64," in image_url else ("image/jpeg", "")
                        media_type = media_type.replace("data:", "")
                        anthropic_messages.append({
                            "role": msg["role"],
                            "content": [
                                {"type": "text", "text": text},
                                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64_data}},
                            ],
                        })
                    else:
                        anthropic_messages.append({"role": msg["role"], "content": text})
                payload = {
                    "model": model or self._get_model(provider_id),
                    "messages": anthropic_messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            elif provider_id == "google":
                gemini_messages = []
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    text, image_url = _split_content(msg["content"])
                    parts = [{"text": text}]
                    if image_url and ";base64," in image_url:
                        media_type, b64_data = image_url.split(";base64,", 1)
                        media_type = media_type.replace("data:", "")
                        parts.append({"inline_data": {"mime_type": media_type, "data": b64_data}})
                    gemini_messages.append({"role": role, "parts": parts})
                payload = {
                    "contents": gemini_messages,
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                }
            elif provider_id == "cohere":
                last_text, _ = _split_content(messages[-1]["content"]) if messages else ("", None)
                payload = {
                    "model": model or self._get_model(provider_id),
                    "message": last_text,
                    "chat_history": [
                        {"role": m["role"], "message": _split_content(m["content"])[0]} for m in messages[:-1]
                    ],
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

    # Providers whose chat endpoint speaks OpenAI-compatible SSE (`data: {...}` lines,
    # `choices[0].delta.content`, terminated by `data: [DONE]`) - real token streaming
    # is only implemented for these. Anthropic/Google/Cohere have their own streaming
    # formats; rather than build three more parsers right now, streaming for them
    # falls back to one non-streamed chunk (see stream_chat_completion below).
    SSE_COMPATIBLE_PROVIDERS = {"groq", "openai", "mistral", "xai", "openrouter", "kimi", "huggingface", "ollama"}

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream a chat completion, yielding {"delta": text} chunks, optional
        {"tool_call": {"name", "arguments"}} events when a tool is invoked, then a
        final {"done": True, "model", "provider", "usage"} event, or {"error": message}.

        When the model requests a tool call, it's executed locally (see tools.py)
        and the result is fed back for a follow-up turn - up to a few rounds - so
        the whole thing still reads as one continuous stream to the caller.
        """
        provider_id = await self._get_active_provider()

        if not provider_id:
            yield {"error": "No AI provider available. Please configure an API key in Settings."}
            return

        api_key = self._get_api_key(provider_id)
        if not api_key and provider_id != "ollama":
            yield {"error": f"{provider_id} API key not configured. Please add it in Settings."}
            return

        if provider_id not in self.SSE_COMPATIBLE_PROVIDERS:
            # no streaming (or tool-calling) parser for this provider yet - fall back to one full chunk
            result = await self.chat_completion(messages, model=model, temperature=temperature, max_tokens=max_tokens)
            if not result.get("success"):
                yield {"error": result.get("error", "Request failed")}
                return
            yield {"delta": result["content"]}
            yield {"done": True, "model": result.get("model"), "provider": provider_id, "usage": result.get("usage", {})}
            return

        from app.services.tools import execute_tool

        base_url = self._get_base_url(provider_id)
        config = self.PROVIDERS[provider_id]
        resolved_model = model or self._get_model(provider_id)
        conversation = list(messages)
        usage: Dict[str, Any] = {}

        try:
            async with httpx.AsyncClient(
                base_url=base_url,
                headers=config["headers"](api_key or ""),
                timeout=120.0,
            ) as client:
                for _round in range(4):  # cap tool round-trips to avoid infinite loops
                    payload = {
                        "model": resolved_model,
                        "messages": conversation,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    }
                    if tools:
                        payload["tools"] = tools
                        payload["tool_choice"] = "auto"

                    full_content = ""
                    tool_calls_acc: Dict[int, Dict[str, str]] = {}
                    finish_reason = None

                    async with client.stream("POST", config["chat_endpoint"], json=payload) as response:
                        if response.status_code >= 400:
                            body = (await response.aread()).decode("utf-8", errors="replace")
                            error_msg = f"HTTP {response.status_code}: {body[:200]}"
                            if response.status_code == 401:
                                error_msg = f"Invalid API key for {provider_id}. Please check your settings."
                            elif response.status_code == 429:
                                error_msg = f"Rate limit exceeded for {provider_id}. Please try again later."
                            self._metrics["errors"] += 1
                            yield {"error": error_msg}
                            return

                        async for line in response.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            data = line[len("data: "):].strip()
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                            except json.JSONDecodeError:
                                continue
                            choice = chunk.get("choices", [{}])[0]
                            delta = choice.get("delta", {})

                            if delta.get("content"):
                                full_content += delta["content"]
                                yield {"delta": delta["content"]}

                            for tc in delta.get("tool_calls", []) or []:
                                idx = tc.get("index", 0)
                                entry = tool_calls_acc.setdefault(idx, {"id": "", "name": "", "arguments": ""})
                                if tc.get("id"):
                                    entry["id"] = tc["id"]
                                fn = tc.get("function", {})
                                if fn.get("name"):
                                    entry["name"] = fn["name"]
                                if fn.get("arguments"):
                                    entry["arguments"] += fn["arguments"]

                            if choice.get("finish_reason"):
                                finish_reason = choice["finish_reason"]
                            if chunk.get("usage"):
                                usage = chunk["usage"]

                    if finish_reason != "tool_calls" or not tool_calls_acc:
                        self._metrics["requests"] += 1
                        self._metrics["provider_usage"][provider_id] = self._metrics["provider_usage"].get(provider_id, 0) + 1
                        yield {"done": True, "model": resolved_model, "provider": provider_id, "usage": usage}
                        return

                    # model wants to call one or more tools - run them, then loop for the follow-up turn
                    ordered_calls = [tool_calls_acc[i] for i in sorted(tool_calls_acc)]
                    conversation.append({
                        "role": "assistant",
                        "content": full_content or None,
                        "tool_calls": [
                            {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                            for tc in ordered_calls
                        ],
                    })
                    for tc in ordered_calls:
                        yield {"tool_call": {"name": tc["name"], "arguments": tc["arguments"]}}
                        result_json = await execute_tool(tc["name"], tc["arguments"])
                        conversation.append({"role": "tool", "tool_call_id": tc["id"], "content": result_json})

                # ran out of rounds - surface whatever the model has said so far as the final answer
                yield {"done": True, "model": resolved_model, "provider": provider_id, "usage": usage}

        except Exception as e:
            self._metrics["errors"] += 1
            yield {"error": f"{provider_id} error: {str(e)}"}

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


# ============================================
# ALIASES for backward compatibility
# ============================================
UnifiedAIService = MultiProviderAIService

async def get_unified_ai_service() -> MultiProviderAIService:
    """Alias for get_multi_provider_service."""
    return await get_multi_provider_service()
