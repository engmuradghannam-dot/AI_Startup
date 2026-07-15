"""AI Chat API routes - Connects to multiple AI providers with fallback."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import httpx
import json

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

# AI Provider configurations with their env var names
AI_PROVIDERS = {
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it"],
        "env_keys": ["GROQ_API_KEY", "GROQ_API_key", "groq_api_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "env_keys": ["OPENAI_API_KEY", "OPENAI_API_key", "openai_api_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    "chatgpt": {
        "name": "ChatGPT (OpenAI)",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "env_keys": ["OPENAI_API_KEY", "CHATGPT_API_KEY", "OPENAI_API_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    "grok": {
        "name": "Grok (xAI)",
        "base_url": "https://api.x.ai/v1",
        "models": ["grok-beta", "grok-vision-beta"],
        "env_keys": ["XAI_API_KEY", "GROK_API_KEY", "XAI_API_key", "GROK_API_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "env_keys": ["ANTHROPIC_API_KEY", "ANTHROPIC_API_key", "anthropic_api_key"],
        "header_format": "x-api-key",
        "enabled": True,
    },
    "google": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        "env_keys": ["GOOGLE_API_KEY", "GOOGLE_API_key", "GEMINI_API_KEY", "google_api_key"],
        "header_format": "query",
        "enabled": True,
    },
    "cohere": {
        "name": "Cohere",
        "base_url": "https://api.cohere.com/v1",
        "models": ["command-r-plus", "command-r", "command"],
        "env_keys": ["COHERE_API_KEY", "COHERE_API_key", "cohere_api_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    "mistral": {
        "name": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
        "env_keys": ["MISTRAL_API_KEY", "MISTRAL_API_key", "mistral_api_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    "kimi": {
        "name": "KIMI (Moonshot AI)",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["kimi-k2", "kimi-k1.5", "kimi-moonshot-v1-8k"],
        "env_keys": ["KIMI_API_KEY", "MOONSHOT_API_KEY", "KIMI_API_key", "MOONSHOT_API_key"],
        "header_format": "bearer",
        "enabled": True,
    },
    # FREE FALLBACK: OpenRouter (free tier available)
    "openrouter": {
        "name": "OpenRouter (Free Tier)",
        "base_url": "https://openrouter.ai/api/v1",
        "models": ["meta-llama/llama-3.1-70b-instruct:free", "google/gemma-2-9b-it:free", "nousresearch/hermes-3-llama-3.1-405b:free"],
        "env_keys": ["OPENROUTER_API_KEY", "OPENROUTER_API_key", "openrouter_api_key"],
        "header_format": "bearer",
        "enabled": True,
        "free": True,
    },
    # FREE FALLBACK: AI21
    "ai21": {
        "name": "AI21 Labs",
        "base_url": "https://api.ai21.com/studio/v1",
        "models": ["jamba-1.5-large", "jamba-1.5-mini"],
        "env_keys": ["AI21_API_KEY", "AI21_API_key", "ai21_api_key"],
        "header_format": "bearer",
        "enabled": True,
    },
}


def get_api_key_for_provider(provider_id: str, request_api_key: Optional[str] = None) -> str:
    """Get API key for a specific provider from request or environment variables."""
    if request_api_key:
        return request_api_key

    provider_config = AI_PROVIDERS.get(provider_id)
    if not provider_config:
        return ""

    for env_key in provider_config["env_keys"]:
        key = os.getenv(env_key)
        if key:
            return key

    return ""


def get_working_provider(preferred: str = "groq") -> tuple:
    """Find a working provider with valid API key."""
    # First try preferred
    if preferred in AI_PROVIDERS:
        key = get_api_key_for_provider(preferred)
        if key:
            return preferred, key

    # Try all providers in order
    for provider_id, config in AI_PROVIDERS.items():
        if not config.get("enabled", True):
            continue
        key = get_api_key_for_provider(provider_id)
        if key:
            return provider_id, key

    return None, ""


class ChatRequest(BaseModel):
    provider: str = "groq"
    model: str = "llama-3.1-70b-versatile"
    messages: List[dict]
    agent_name: str = "AI Agent"
    api_key: Optional[str] = None
    auto_fallback: bool = True  # Try other providers if preferred fails


@router.get("/providers")
async def get_providers():
    """Get all available AI providers and their API key status."""
    result = {}
    for provider_id, config in AI_PROVIDERS.items():
        api_key = get_api_key_for_provider(provider_id)
        result[provider_id] = {
            "name": config["name"],
            "models": config["models"],
            "has_key": bool(api_key),
            "env_keys": config["env_keys"],
            "free": config.get("free", False),
        }
    return result


async def call_openai_compatible(client: httpx.AsyncClient, provider_id: str, provider_config: dict, 
                                api_key: str, model: str, messages: list, agent_name: str) -> dict:
    """Call OpenAI-compatible API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # OpenRouter needs extra headers
    if provider_id == "openrouter":
        headers["HTTP-Referer"] = "https://ai-startup.app"
        headers["X-Title"] = "AI Startup"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    try:
        response = await client.post(
            f"{provider_config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
        )

        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return {
                "response": ai_response,
                "provider": provider_id,
                "model": model,
                "mock": False,
            }
        elif response.status_code == 401:
            return {
                "response": None,  # Signal to try fallback
                "error": f"401 Unauthorized - {provider_config['name']}",
                "fallback": True,
            }
        else:
            error_text = response.text[:300]
            return {
                "response": None,
                "error": f"{response.status_code}: {error_text}",
                "fallback": True,
            }
    except Exception as e:
        return {
            "response": None,
            "error": str(e),
            "fallback": True,
        }


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send message to AI and get response with auto-fallback."""
    try:
        provider_id = request.provider
        model = request.model
        messages = request.messages
        agent_name = request.agent_name
        auto_fallback = request.auto_fallback

        # Get API key for preferred provider
        api_key = get_api_key_for_provider(provider_id, request.api_key)

        # If no key for preferred, try auto-fallback to any working provider
        if not api_key and auto_fallback:
            fallback_provider, fallback_key = get_working_provider()
            if fallback_provider:
                provider_id = fallback_provider
                api_key = fallback_key
                model = AI_PROVIDERS[fallback_provider]["models"][0]  # Use first available model

        if not api_key:
            provider_config = AI_PROVIDERS.get(provider_id)
            env_keys_str = ", ".join(provider_config["env_keys"]) if provider_config else "GROQ_API_KEY"
            return {
                "response": f"{agent_name}: No API key found. Please add one of these environment variables in Railway: {env_keys_str}. Or use OpenRouter (free) by setting OPENROUTER_API_KEY.",
                "provider": provider_id,
                "model": model,
                "mock": True,
                "error": f"No API key. Set env var: {env_keys_str}",
            }

        provider_config = AI_PROVIDERS.get(provider_id)
        if not provider_config:
            return {
                "response": f"{agent_name}: Unknown provider: {provider_id}",
                "provider": provider_id,
                "model": model,
                "mock": True,
                "error": "Unknown provider",
            }

        # Call the AI API
        async with httpx.AsyncClient(timeout=60.0) as client:
            # OpenAI-compatible providers
            if provider_id in ["groq", "openai", "chatgpt", "mistral", "grok", "kimi", "cohere", "openrouter", "ai21"]:
                result = await call_openai_compatible(client, provider_id, provider_config, api_key, model, messages, agent_name)

                # If failed and auto_fallback enabled, try other providers
                if result.get("fallback") and auto_fallback:
                    tried = [provider_id]
                    for fallback_id, fallback_config in AI_PROVIDERS.items():
                        if fallback_id in tried or not fallback_config.get("enabled", True):
                            continue
                        fallback_key = get_api_key_for_provider(fallback_id)
                        if not fallback_key:
                            continue

                        fallback_model = fallback_config["models"][0]
                        fallback_result = await call_openai_compatible(
                            client, fallback_id, fallback_config, fallback_key, fallback_model, messages, agent_name
                        )

                        if not fallback_result.get("fallback"):
                            fallback_result["original_provider"] = provider_id
                            fallback_result["fallback_provider"] = fallback_id
                            return fallback_result

                        tried.append(fallback_id)

                    # All providers failed
                    return {
                        "response": f"{agent_name}: All AI providers failed. Last error: {result.get('error', 'Unknown')}. Please check your API keys in Railway Settings > Variables.",
                        "provider": provider_id,
                        "model": model,
                        "mock": True,
                        "error": result.get("error", "All providers failed"),
                    }

                return result if not result.get("fallback") else {
                    "response": f"{agent_name}: Error - {result.get('error', 'Unknown')}",
                    "provider": provider_id,
                    "model": model,
                    "mock": True,
                    "error": result.get("error"),
                }

            elif provider_id == "anthropic":
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                }

                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": 2048,
                }

                try:
                    response = await client.post(
                        f"{provider_config['base_url']}/messages",
                        headers=headers,
                        json=payload,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["content"][0]["text"]
                        return {
                            "response": ai_response,
                            "provider": provider_id,
                            "model": model,
                            "mock": False,
                        }
                    else:
                        return {
                            "response": f"{agent_name}: Error from {provider_config['name']}: {response.status_code}",
                            "provider": provider_id,
                            "model": model,
                            "mock": True,
                            "error": response.text[:300],
                        }
                except Exception as e:
                    return {
                        "response": f"{agent_name}: Connection error: {str(e)[:100]}",
                        "provider": provider_id,
                        "model": model,
                        "mock": True,
                        "error": str(e),
                    }

            elif provider_id == "google":
                headers = {
                    "Content-Type": "application/json",
                }

                gemini_messages = []
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})

                payload = {
                    "contents": gemini_messages,
                }

                try:
                    response = await client.post(
                        f"{provider_config['base_url']}/models/{model}:generateContent?key={api_key}",
                        headers=headers,
                        json=payload,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "response": ai_response,
                            "provider": provider_id,
                            "model": model,
                            "mock": False,
                        }
                    else:
                        return {
                            "response": f"{agent_name}: Error from {provider_config['name']}: {response.status_code}",
                            "provider": provider_id,
                            "model": model,
                            "mock": True,
                            "error": response.text[:300],
                        }
                except Exception as e:
                    return {
                        "response": f"{agent_name}: Connection error: {str(e)[:100]}",
                        "provider": provider_id,
                        "model": model,
                        "mock": True,
                        "error": str(e),
                    }

            else:
                return {
                    "response": f"{agent_name}: Provider {provider_config['name']} integration coming soon!",
                    "provider": provider_id,
                    "model": model,
                    "mock": True,
                }

    except Exception as e:
        return {
            "response": f"{agent_name}: System error: {str(e)[:200]}",
            "provider": request.provider if hasattr(request, 'provider') else "unknown",
            "model": request.model if hasattr(request, 'model') else "unknown",
            "mock": True,
            "error": str(e),
        }
