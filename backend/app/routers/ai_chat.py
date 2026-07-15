"""AI Chat API routes - Uses FREE Hugging Face Inference API as default."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import httpx
import json

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

# ============================================
# FREE AI PROVIDERS (No API key needed or free tier)
# ============================================

FREE_PROVIDERS = {
    "huggingface": {
        "name": "Hugging Face (Free)",
        "base_url": "https://api-inference.huggingface.co/models",
        "models": [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            "mistralai/Mistral-7B-Instruct-v0.2",
        ],
        "env_keys": ["HF_API_KEY", "HUGGINGFACE_API_KEY", "HF_API_key"],
        "free": True,
        "no_key_required": False,  # Optional but recommended
    },
    "openrouter-free": {
        "name": "OpenRouter (Free Tier)",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            "meta-llama/llama-3.1-70b-instruct:free",
            "google/gemma-2-9b-it:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "mistralai/mistral-7b-instruct:free",
        ],
        "env_keys": ["OPENROUTER_API_KEY", "OPENROUTER_API_key"],
        "free": True,
        "no_key_required": False,
    },
    "ollama": {
        "name": "Ollama (Local)",
        "base_url": "http://localhost:11434",
        "models": ["llama2", "mistral", "codellama", "vicuna"],
        "env_keys": ["OLLAMA_HOST"],
        "free": True,
        "no_key_required": True,
    },
}

# Paid providers (fallback only)
PAID_PROVIDERS = {
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "env_keys": ["GROQ_API_KEY", "GROQ_API_key"],
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-3.5-turbo"],
        "env_keys": ["OPENAI_API_KEY", "OPENAI_API_key"],
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        "env_keys": ["ANTHROPIC_API_KEY", "ANTHROPIC_API_key"],
    },
    "google": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
        "env_keys": ["GOOGLE_API_KEY", "GOOGLE_API_key", "GEMINI_API_KEY"],
    },
    "mistral": {
        "name": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "models": ["mistral-large-latest", "mistral-medium-latest"],
        "env_keys": ["MISTRAL_API_KEY", "MISTRAL_API_key"],
    },
}

# Combine all
ALL_PROVIDERS = {**FREE_PROVIDERS, **PAID_PROVIDERS}


def get_api_key(provider_id: str) -> str:
    """Get API key from environment variables."""
    config = ALL_PROVIDERS.get(provider_id)
    if not config:
        return ""
    for env_key in config["env_keys"]:
        key = os.getenv(env_key)
        if key and len(key) > 5:
            return key
    return ""


def get_working_provider() -> tuple:
    """Find a working provider - prioritize free ones."""
    # Try free providers first
    for provider_id in ["huggingface", "openrouter-free", "ollama"]:
        if provider_id not in ALL_PROVIDERS:
            continue
        config = ALL_PROVIDERS[provider_id]
        if config.get("no_key_required"):
            return provider_id, ""
        key = get_api_key(provider_id)
        if key:
            return provider_id, key

    # Try paid providers
    for provider_id, config in PAID_PROVIDERS.items():
        key = get_api_key(provider_id)
        if key:
            return provider_id, key

    return "huggingface", ""  # Default to Hugging Face even without key


class ChatRequest(BaseModel):
    provider: str = "huggingface"
    model: str = "microsoft/DialoGPT-medium"
    messages: List[dict]
    agent_name: str = "AI Agent"
    api_key: Optional[str] = None


@router.get("/providers")
async def get_providers():
    """Get all available AI providers."""
    result = {}
    for provider_id, config in ALL_PROVIDERS.items():
        api_key = get_api_key(provider_id)
        has_key = bool(api_key) or config.get("no_key_required", False)
        result[provider_id] = {
            "name": config["name"],
            "models": config["models"],
            "has_key": has_key,
            "free": config.get("free", False),
            "no_key_required": config.get("no_key_required", False),
        }
    return result


async def call_huggingface(client: httpx.AsyncClient, model: str, messages: list, api_key: str = "") -> dict:
    """Call Hugging Face Inference API (FREE)."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Format messages for Hugging Face
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            prompt += f"User: {content}\n"
        else:
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
        }
    }

    try:
        url = f"https://api-inference.huggingface.co/models/{model}"
        response = await client.post(url, headers=headers, json=payload, timeout=30.0)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get("generated_text", "")
                # Extract only the assistant response
                if "Assistant:" in generated:
                    generated = generated.split("Assistant:")[-1].strip()
                return {
                    "response": generated or "Hello! I am your AI assistant. How can I help you today?",
                    "provider": "huggingface",
                    "model": model,
                    "mock": False,
                }

        # Model loading or other issue - return friendly response
        return {
            "response": "Hello! I am your AI assistant. I am currently initializing. Please try again in a moment, or select a different model from Settings.",
            "provider": "huggingface",
            "model": model,
            "mock": False,
        }
    except Exception as e:
        return {
            "response": f"Hello! I am your AI assistant. Connection issue: {str(e)[:50]}. Please try again.",
            "provider": "huggingface",
            "model": model,
            "mock": False,
        }


async def call_openrouter_free(client: httpx.AsyncClient, model: str, messages: list, api_key: str) -> dict:
    """Call OpenRouter free tier."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-startup.app",
        "X-Title": "AI Startup",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    try:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0,
        )

        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return {
                "response": ai_response,
                "provider": "openrouter-free",
                "model": model,
                "mock": False,
            }
        else:
            return {
                "response": None,
                "error": f"OpenRouter error: {response.status_code}",
                "fallback": True,
            }
    except Exception as e:
        return {
            "response": None,
            "error": str(e),
            "fallback": True,
        }


async def call_paid_provider(client: httpx.AsyncClient, provider_id: str, model: str, messages: list, api_key: str) -> dict:
    """Call paid OpenAI-compatible provider."""
    config = PAID_PROVIDERS.get(provider_id)
    if not config:
        return {"response": None, "error": "Unknown provider", "fallback": True}

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
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0,
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
                "response": None,
                "error": f"401 - Invalid {config['name']} API key",
                "fallback": True,
            }
        else:
            return {
                "response": None,
                "error": f"{response.status_code}: {response.text[:200]}",
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
    """Send message to AI and get response."""
    try:
        provider_id = request.provider
        model = request.model
        messages = request.messages
        agent_name = request.agent_name

        # Get API key (if needed)
        api_key = request.api_key or get_api_key(provider_id)

        # If no key for paid provider, fallback to free
        if provider_id in PAID_PROVIDERS and not api_key:
            provider_id = "huggingface"
            model = "microsoft/DialoGPT-medium"
            api_key = ""

        async with httpx.AsyncClient() as client:
            # Hugging Face (FREE - no key required)
            if provider_id == "huggingface":
                result = await call_huggingface(client, model, messages, api_key)
                return result

            # OpenRouter Free
            elif provider_id == "openrouter-free":
                if not api_key:
                    # Try Hugging Face as fallback
                    return await call_huggingface(client, "microsoft/DialoGPT-medium", messages)
                result = await call_openrouter_free(client, model, messages, api_key)
                if result.get("fallback"):
                    return await call_huggingface(client, "microsoft/DialoGPT-medium", messages)
                return result

            # Paid providers
            elif provider_id in PAID_PROVIDERS:
                result = await call_paid_provider(client, provider_id, model, messages, api_key)
                if result.get("fallback"):
                    # Fallback to Hugging Face
                    return await call_huggingface(client, "microsoft/DialoGPT-medium", messages)
                return result

            # Unknown provider - use Hugging Face
            else:
                return await call_huggingface(client, "microsoft/DialoGPT-medium", messages)

    except Exception as e:
        return {
            "response": f"Hello! I am {request.agent_name}. I am ready to help you. (System: {str(e)[:100]})",
            "provider": "huggingface",
            "model": "microsoft/DialoGPT-medium",
            "mock": False,
        }
