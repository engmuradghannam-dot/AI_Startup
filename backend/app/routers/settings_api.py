"""Settings API routes for managing AI provider configurations."""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os

router = APIRouter(prefix="/settings", tags=["Settings"])


# ========== Pydantic Models ==========

class AIProviderConfig(BaseModel):
    id: str
    name: str
    api_key: str
    base_url: str
    default_model: str
    is_active: bool = False
    temperature: float = 0.7
    max_tokens: int = 2048


class SettingsResponse(BaseModel):
    providers: List[AIProviderConfig]
    active_provider: Optional[str] = None
    llm_mode: str = "auto"


class UpdateProviderRequest(BaseModel):
    api_key: str
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    is_active: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


# ========== In-memory storage (replace with DB in production) ==========

_default_providers = {
    "groq": {
        "id": "groq",
        "name": "Groq",
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-70b-versatile",
        "is_active": bool(os.getenv("GROQ_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "is_active": bool(os.getenv("OPENAI_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "google": {
        "id": "google",
        "name": "Google Gemini",
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "default_model": "gemini-1.5-pro",
        "is_active": bool(os.getenv("GOOGLE_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-sonnet-20241022",
        "is_active": bool(os.getenv("ANTHROPIC_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "mistral": {
        "id": "mistral",
        "name": "Mistral AI",
        "api_key": os.getenv("MISTRAL_API_KEY", ""),
        "base_url": "https://api.mistral.ai/v1",
        "default_model": "mistral-large-latest",
        "is_active": bool(os.getenv("MISTRAL_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "cohere": {
        "id": "cohere",
        "name": "Cohere",
        "api_key": os.getenv("COHERE_API_KEY", ""),
        "base_url": "https://api.cohere.com/v1",
        "default_model": "command-r-plus",
        "is_active": bool(os.getenv("COHERE_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "ollama": {
        "id": "ollama",
        "name": "Ollama (Local)",
        "api_key": "local",
        "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "default_model": "llama3",
        "is_active": False,
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "huggingface": {
        "id": "huggingface",
        "name": "Hugging Face (FREE)",
        "api_key": os.getenv("HF_API_KEY", ""),
        "base_url": "https://api-inference.huggingface.co/models",
        "default_model": "mistralai/Mistral-7B-Instruct-v0.2",
        "is_active": bool(os.getenv("HF_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter",
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "meta-llama/llama-3.1-70b-instruct:free",
        "is_active": bool(os.getenv("OPENROUTER_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "xai": {
        "id": "xai",
        "name": "xAI (Grok)",
        "api_key": os.getenv("XAI_API_KEY", ""),
        "base_url": "https://api.x.ai/v1",
        "default_model": "grok-beta",
        "is_active": bool(os.getenv("XAI_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "kimi": {
        "id": "kimi",
        "name": "KIMI (Moonshot)",
        "api_key": os.getenv("KIMI_API_KEY", ""),
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "is_active": bool(os.getenv("KIMI_API_KEY", "")),
        "temperature": 0.7,
        "max_tokens": 2048,
    },
}

_providers: Dict[str, dict] = dict(_default_providers)
_active_provider: Optional[str] = None
_llm_mode: str = "auto"


def _get_active_provider_id() -> Optional[str]:
    """Get the first active provider."""
    global _active_provider
    if _active_provider and _providers.get(_active_provider, {}).get("is_active"):
        return _active_provider
    for pid, provider in _providers.items():
        if provider.get("is_active") and provider.get("api_key"):
            _active_provider = pid
            return pid
    return None


# ========== Routes ==========

@router.get("/providers", response_model=List[AIProviderConfig])
async def get_providers():
    """Get all AI provider configurations."""
    return [AIProviderConfig(**p) for p in _providers.values()]


@router.get("/providers/{provider_id}", response_model=AIProviderConfig)
async def get_provider(provider_id: str):
    """Get a specific provider configuration."""
    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    return AIProviderConfig(**_providers[provider_id])


@router.patch("/providers/{provider_id}", response_model=AIProviderConfig)
async def update_provider(provider_id: str, request: UpdateProviderRequest):
    """Update a provider configuration."""
    global _active_provider

    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider = _providers[provider_id]

    if request.api_key is not None:
        provider["api_key"] = request.api_key
    if request.base_url is not None:
        provider["base_url"] = request.base_url
    if request.default_model is not None:
        provider["default_model"] = request.default_model
    if request.is_active is not None:
        provider["is_active"] = request.is_active
        if request.is_active:
            _active_provider = provider_id
            # Deactivate others if this one is activated
            for pid, p in _providers.items():
                if pid != provider_id:
                    p["is_active"] = False
    if request.temperature is not None:
        provider["temperature"] = request.temperature
    if request.max_tokens is not None:
        provider["max_tokens"] = request.max_tokens

    return AIProviderConfig(**provider)


@router.post("/providers/{provider_id}/test")
async def test_provider(provider_id: str):
    """Test a provider connection."""
    import httpx

    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider = _providers[provider_id]
    api_key = provider.get("api_key", "")

    if not api_key or api_key == "local":
        return {"success": False, "message": "No API key configured"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider_id == "groq":
                response = await client.get(
                    f"{provider['base_url']}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
            elif provider_id == "openai":
                response = await client.get(
                    f"{provider['base_url']}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
            elif provider_id == "google":
                response = await client.get(
                    f"{provider['base_url']}/models?key={api_key}"
                )
            elif provider_id == "anthropic":
                response = await client.get(
                    f"{provider['base_url']}/models",
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"}
                )
            else:
                return {"success": True, "message": f"Test not implemented for {provider_id}"}

            if response.status_code == 200:
                data = response.json()
                models = data.get("data", []) if isinstance(data, dict) else []
                return {
                    "success": True,
                    "message": f"Connected successfully! {len(models)} models available.",
                    "models_count": len(models),
                }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}: {response.text[:200]}",
                }
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


@router.get("/active-provider")
async def get_active_provider():
    """Get the currently active provider."""
    active_id = _get_active_provider_id()
    if not active_id:
        return {"provider": None, "message": "No active provider configured"}
    return {"provider": AIProviderConfig(**_providers[active_id])}


@router.post("/active-provider/{provider_id}")
async def set_active_provider(provider_id: str):
    """Set the active provider."""
    global _active_provider

    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")

    if not _providers[provider_id].get("api_key"):
        raise HTTPException(status_code=400, detail="Provider has no API key configured")

    _active_provider = provider_id
    for pid, p in _providers.items():
        p["is_active"] = (pid == provider_id)

    return {"message": f"{provider_id} is now the active provider"}


@router.get("/llm-mode")
async def get_llm_mode():
    """Get current LLM mode."""
    return {"mode": _llm_mode}


@router.post("/llm-mode/{mode}")
async def set_llm_mode(mode: str):
    """Set LLM mode: auto, cloud, local."""
    global _llm_mode
    if mode not in ["auto", "cloud", "local"]:
        raise HTTPException(status_code=400, detail="Mode must be auto, cloud, or local")
    _llm_mode = mode
    return {"message": f"LLM mode set to {mode}"}
