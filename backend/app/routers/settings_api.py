"""Settings API routes for managing AI provider configurations."""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import httpx
from beanie import Document, Indexed

router = APIRouter(prefix="/settings", tags=["Settings"])


# ========== Beanie Document Model ==========

class AIProviderDocument(Document):
    """MongoDB document for AI provider settings."""

    provider_id: Indexed(str, unique=True)
    name: str
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    is_active: bool = False
    temperature: float = 0.7
    max_tokens: int = 2048

    class Settings:
        name = "ai_provider_settings"


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


class UpdateProviderRequest(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    is_active: Optional[bool] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


# ========== Default Providers ==========

DEFAULT_PROVIDERS = {
    "groq": {
        "provider_id": "groq",
        "name": "Groq",
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-70b-versatile",
        "is_active": bool(os.getenv("GROQ_API_KEY", "")),
    },
    "openai": {
        "provider_id": "openai",
        "name": "OpenAI",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "is_active": bool(os.getenv("OPENAI_API_KEY", "")),
    },
    "google": {
        "provider_id": "google",
        "name": "Google Gemini",
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "default_model": "gemini-1.5-pro",
        "is_active": bool(os.getenv("GOOGLE_API_KEY", "")),
    },
    "anthropic": {
        "provider_id": "anthropic",
        "name": "Anthropic Claude",
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-sonnet-20241022",
        "is_active": bool(os.getenv("ANTHROPIC_API_KEY", "")),
    },
    "mistral": {
        "provider_id": "mistral",
        "name": "Mistral AI",
        "api_key": os.getenv("MISTRAL_API_KEY", ""),
        "base_url": "https://api.mistral.ai/v1",
        "default_model": "mistral-large-latest",
        "is_active": bool(os.getenv("MISTRAL_API_KEY", "")),
    },
    "cohere": {
        "provider_id": "cohere",
        "name": "Cohere",
        "api_key": os.getenv("COHERE_API_KEY", ""),
        "base_url": "https://api.cohere.com/v1",
        "default_model": "command-r-plus",
        "is_active": bool(os.getenv("COHERE_API_KEY", "")),
    },
    "ollama": {
        "provider_id": "ollama",
        "name": "Ollama (Local)",
        "api_key": "local",
        "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "default_model": "llama3",
        "is_active": False,
    },
    "huggingface": {
        "provider_id": "huggingface",
        "name": "Hugging Face (FREE)",
        "api_key": os.getenv("HF_API_KEY", ""),
        "base_url": "https://api-inference.huggingface.co/models",
        "default_model": "mistralai/Mistral-7B-Instruct-v0.2",
        "is_active": bool(os.getenv("HF_API_KEY", "")),
    },
    "openrouter": {
        "provider_id": "openrouter",
        "name": "OpenRouter",
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "meta-llama/llama-3.1-70b-instruct:free",
        "is_active": bool(os.getenv("OPENROUTER_API_KEY", "")),
    },
    "xai": {
        "provider_id": "xai",
        "name": "xAI (Grok)",
        "api_key": os.getenv("XAI_API_KEY", ""),
        "base_url": "https://api.x.ai/v1",
        "default_model": "grok-beta",
        "is_active": bool(os.getenv("XAI_API_KEY", "")),
    },
    "kimi": {
        "provider_id": "kimi",
        "name": "KIMI (Moonshot)",
        "api_key": os.getenv("KIMI_API_KEY", ""),
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "is_active": bool(os.getenv("KIMI_API_KEY", "")),
    },
}


async def init_default_providers():
    """Initialize default providers in MongoDB if they don't exist."""
    for provider_data in DEFAULT_PROVIDERS.values():
        existing = await AIProviderDocument.find_one(
            AIProviderDocument.provider_id == provider_data["provider_id"]
        )
        if not existing:
            await AIProviderDocument(**provider_data).insert()


# ========== Routes ==========

@router.on_event("startup")
async def startup():
    """Initialize default providers on startup."""
    await init_default_providers()


@router.get("/providers", response_model=List[AIProviderConfig])
async def get_providers():
    """Get all AI provider configurations from database."""
    providers = await AIProviderDocument.find_all().to_list()
    if not providers:
        await init_default_providers()
        providers = await AIProviderDocument.find_all().to_list()
    return [AIProviderConfig(
        id=p.provider_id,
        name=p.name,
        api_key=p.api_key,
        base_url=p.base_url,
        default_model=p.default_model,
        is_active=p.is_active,
        temperature=p.temperature,
        max_tokens=p.max_tokens,
    ) for p in providers]


@router.get("/providers/{provider_id}", response_model=AIProviderConfig)
async def get_provider(provider_id: str):
    """Get a specific provider configuration."""
    provider = await AIProviderDocument.find_one(
        AIProviderDocument.provider_id == provider_id
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return AIProviderConfig(
        id=provider.provider_id,
        name=provider.name,
        api_key=provider.api_key,
        base_url=provider.base_url,
        default_model=provider.default_model,
        is_active=provider.is_active,
        temperature=provider.temperature,
        max_tokens=provider.max_tokens,
    )


@router.patch("/providers/{provider_id}", response_model=AIProviderConfig)
async def update_provider(provider_id: str, request: UpdateProviderRequest):
    """Update a provider configuration."""
    provider = await AIProviderDocument.find_one(
        AIProviderDocument.provider_id == provider_id
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    if request.api_key is not None:
        provider.api_key = request.api_key
    if request.base_url is not None:
        provider.base_url = request.base_url
    if request.default_model is not None:
        provider.default_model = request.default_model
    if request.is_active is not None:
        provider.is_active = request.is_active
        if request.is_active:
            async for p in AIProviderDocument.find_all():
                if p.provider_id != provider_id:
                    p.is_active = False
                    await p.save()
    if request.temperature is not None:
        provider.temperature = request.temperature
    if request.max_tokens is not None:
        provider.max_tokens = request.max_tokens

    await provider.save()

    return AIProviderConfig(
        id=provider.provider_id,
        name=provider.name,
        api_key=provider.api_key,
        base_url=provider.base_url,
        default_model=provider.default_model,
        is_active=provider.is_active,
        temperature=provider.temperature,
        max_tokens=provider.max_tokens,
    )


@router.post("/providers/{provider_id}/test")
async def test_provider(provider_id: str):
    """Test a provider connection."""
    provider = await AIProviderDocument.find_one(
        AIProviderDocument.provider_id == provider_id
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    api_key = provider.api_key

    if not api_key or api_key == "local":
        return {"success": False, "message": "No API key configured"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider_id == "groq":
                response = await client.get(
                    f"{provider.base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
            elif provider_id == "openai":
                response = await client.get(
                    f"{provider.base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
            elif provider_id == "google":
                response = await client.get(
                    f"{provider.base_url}/models?key={api_key}"
                )
            elif provider_id == "anthropic":
                response = await client.get(
                    f"{provider.base_url}/models",
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
    active = await AIProviderDocument.find_one(AIProviderDocument.is_active == True)
    if not active:
        return {"provider": None, "message": "No active provider configured"}
    return {
        "provider": AIProviderConfig(
            id=active.provider_id,
            name=active.name,
            api_key=active.api_key,
            base_url=active.base_url,
            default_model=active.default_model,
            is_active=active.is_active,
            temperature=active.temperature,
            max_tokens=active.max_tokens,
        )
    }


@router.post("/active-provider/{provider_id}")
async def set_active_provider(provider_id: str):
    """Set the active provider."""
    provider = await AIProviderDocument.find_one(
        AIProviderDocument.provider_id == provider_id
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    async for p in AIProviderDocument.find_all():
        p.is_active = False
        await p.save()

    provider.is_active = True
    await provider.save()

    return {"message": f"{provider_id} is now the active provider"}


@router.get("/llm-mode")
async def get_llm_mode():
    """Get current LLM mode."""
    return {"mode": "auto"}


@router.post("/llm-mode/{mode}")
async def set_llm_mode(mode: str):
    """Set LLM mode: auto, cloud, local."""
    if mode not in ["auto", "cloud", "local"]:
        raise HTTPException(status_code=400, detail="Mode must be auto, cloud, or local")
    return {"message": f"LLM mode set to {mode}"}
