"""Local LLM Management API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.local_llm_service import get_local_llm_service, AVAILABLE_MODELS

router = APIRouter(prefix="/local-llm", tags=["Local LLM"])


class PullModelRequest(BaseModel):
    model_name: str


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048


@router.get("/health")
async def local_llm_health():
    """Check local LLM health status."""
    try:
        service = await get_local_llm_service()
        return await service.health_check()
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "ollama": {"connected": False},
            "localai": {"connected": False},
        }


@router.get("/models")
async def list_local_models():
    """List all available local models."""
    try:
        service = await get_local_llm_service()

        # Get installed models
        installed = service.available_models

        # Get all known models with info
        all_models = []
        for model_id, info in AVAILABLE_MODELS.items():
            all_models.append({
                "id": model_id,
                **info,
                "installed": model_id in installed or any(model_id in m for m in installed),
            })

        return {
            "installed_models": installed,
            "available_models": all_models,
            "provider": service.provider,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.post("/models/pull")
async def pull_model(request: PullModelRequest):
    """Pull a model from Ollama registry."""
    try:
        service = await get_local_llm_service()
        result = await service.pull_model(request.model_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {str(e)}")


@router.post("/generate")
async def generate(request: GenerateRequest):
    """Generate text using local LLM."""
    try:
        service = await get_local_llm_service()
        messages = [{"role": "user", "content": request.prompt}]

        result = await service.generate(
            messages=messages,
            model=request.model,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 2048,
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/models/recommended")
async def recommended_models():
    """Get recommended models for different use cases."""
    return {
        "recommended": [
            {
                "id": "qwen3:0.6b",
                "name": "Qwen3 0.6B",
                "use_case": "Quick responses, simple tasks",
                "ram_mb": 1024,
                "speed": "Very Fast",
            },
            {
                "id": "tinyllama",
                "name": "TinyLlama 1.1B",
                "use_case": "Coding assistance, chatbots",
                "ram_mb": 1536,
                "speed": "Fast",
            },
            {
                "id": "phi4-mini",
                "name": "Phi-4 Mini 3.8B",
                "use_case": "Complex reasoning, agent tasks",
                "ram_mb": 4096,
                "speed": "Moderate",
            },
        ],
        "github_actions_compatible": [
            "qwen3:0.6b",
            "tinyllama",
            "gemma3:1b",
        ],
    }
