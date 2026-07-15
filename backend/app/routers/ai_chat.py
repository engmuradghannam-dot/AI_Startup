"""AI Chat API routes - Connects to multiple AI providers."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import httpx
import json

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

# AI Provider configurations
AI_PROVIDERS = {
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it"],
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "chatgpt": {
        "name": "ChatGPT (OpenAI)",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "grok": {
        "name": "Grok (xAI)",
        "base_url": "https://api.x.ai/v1",
        "models": ["grok-beta", "grok-vision-beta"],
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
    },
    "google": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    },
    "cohere": {
        "name": "Cohere",
        "base_url": "https://api.cohere.com/v1",
        "models": ["command-r-plus", "command-r", "command"],
    },
    "mistral": {
        "name": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
    },
    "kimi": {
        "name": "KIMI (Moonshot AI)",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["kimi-k2", "kimi-k1.5", "kimi-moonshot-v1-8k"],
    },
}


class ChatRequest(BaseModel):
    provider: str = "groq"
    model: str = "llama-3.1-70b-versatile"
    messages: List[dict]
    agent_name: str = "AI Agent"
    api_key: Optional[str] = None


@router.get("/providers")
async def get_providers():
    """Get all available AI providers."""
    return {
        provider_id: {
            "name": config["name"],
            "models": config["models"],
        }
        for provider_id, config in AI_PROVIDERS.items()
    }


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send message to AI and get response."""
    try:
        provider_id = request.provider
        model = request.model
        messages = request.messages
        agent_name = request.agent_name

        # Use API key from request, fallback to env
        api_key = request.api_key or os.getenv("GROQ_API_KEY", "")

        if not api_key:
            return {
                "response": f"{agent_name}: Please configure the API key in Settings. Go to Settings > AI Providers and enter your API key.",
                "provider": provider_id,
                "model": model,
                "mock": True,
                "error": "No API key provided",
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
            if provider_id in ["groq", "openai", "chatgpt", "mistral", "grok", "kimi"]:
                # OpenAI-compatible API
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

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
                    else:
                        error_text = response.text[:200]
                        return {
                            "response": f"{agent_name}: Error from {provider_config['name']}: {response.status_code}. Please check your API key.",
                            "provider": provider_id,
                            "model": model,
                            "mock": True,
                            "error": error_text,
                        }
                except Exception as e:
                    return {
                        "response": f"{agent_name}: Connection error: {str(e)[:100]}. Please try again.",
                        "provider": provider_id,
                        "model": model,
                        "mock": True,
                        "error": str(e),
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
                            "error": response.text[:200],
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
                            "error": response.text[:200],
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
