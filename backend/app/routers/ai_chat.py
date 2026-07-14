"""AI Chat API routes - Connects to multiple AI providers."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request
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
    "grok": {
        "name": "Grok (xAI)",
        "base_url": "https://api.x.ai/v1",
        "models": ["grok-beta", "grok-vision-beta"],
    },
    "chatgpt": {
        "name": "ChatGPT (OpenAI)",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
}


def get_api_key(provider_id: str) -> Optional[str]:
    """Get API key from environment or settings."""
    env_map = {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "cohere": "COHERE_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "grok": "XAI_API_KEY",
        "chatgpt": "OPENAI_API_KEY",
    }
    return os.getenv(env_map.get(provider_id, ""))


@router.get("/providers")
async def get_providers():
    """Get all available AI providers."""
    return {
        provider_id: {
            "name": config["name"],
            "models": config["models"],
            "has_key": get_api_key(provider_id) is not None,
        }
        for provider_id, config in AI_PROVIDERS.items()
    }


@router.post("/chat")
async def chat(request: Request):
    """Send message to AI and get response."""
    try:
        data = await request.json()
        provider_id = data.get("provider", "groq")
        model = data.get("model", "llama-3.1-70b-versatile")
        messages = data.get("messages", [])
        agent_name = data.get("agent_name", "AI Agent")

        api_key = get_api_key(provider_id)

        if not api_key:
            # Return mock response if no API key
            return {
                "response": f"{agent_name}: I\'m currently running in mock mode. Please configure the {AI_PROVIDERS.get(provider_id, {}).get('name', provider_id)} API key in Settings to enable real AI responses.",
                "provider": provider_id,
                "model": model,
                "mock": True,
            }

        provider_config = AI_PROVIDERS.get(provider_id)
        if not provider_config:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_id}")

        # Call the AI API
        async with httpx.AsyncClient(timeout=60.0) as client:
            if provider_id in ["groq", "openai", "chatgpt", "mistral"]:
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
                    return {
                        "response": f"{agent_name}: Error from {provider_config['name']}: {response.status_code} - {response.text}",
                        "provider": provider_id,
                        "model": model,
                        "mock": True,
                    }

            elif provider_id == "anthropic":
                # Anthropic API
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
                    }

            elif provider_id == "google":
                # Google Gemini API
                headers = {
                    "Content-Type": "application/json",
                }

                # Convert messages to Gemini format
                gemini_messages = []
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})

                payload = {
                    "contents": gemini_messages,
                }

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
                    }

            elif provider_id == "grok":
                # xAI Grok API (OpenAI-compatible)
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
                    return {
                        "response": f"{agent_name}: Error from {provider_config['name']}: {response.status_code}",
                        "provider": provider_id,
                        "model": model,
                        "mock": True,
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
            "response": f"Error: {str(e)}",
            "provider": provider_id,
            "model": model if 'model' in locals() else "unknown",
            "mock": True,
        }
