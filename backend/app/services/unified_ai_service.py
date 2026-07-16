"""Unified AI Service - Groq Cloud Primary + Local LLM Optional.

Primary: Groq API (fast, reliable, works everywhere)
Optional: Local LLM (Ollama/LocalAI) for local development
Auto mode: Uses Groq by default, tries local if configured
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.config import get_settings

# Groq is primary
try:
    from app.services.groq_service import get_groq_service
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Local LLM is optional
try:
    from app.services.local_llm_service import get_local_llm_service, LocalLLMService
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedAIService:
    """Unified AI service with Groq-first architecture."""

    def __init__(self):
        self.settings = get_settings()
        self.mode = self.settings.llm_mode
        self._groq_service = None
        self._local_service = None
        self._metrics = {
            "groq_requests": 0,
            "local_requests": 0,
            "fallback_count": 0,
            "errors": 0,
        }

    async def _get_groq_service(self):
        if not GROQ_AVAILABLE:
            return None
        if self._groq_service is None:
            self._groq_service = await get_groq_service()
        return self._groq_service

    async def _get_local_service(self):
        if not LOCAL_AVAILABLE:
            return None
        if self._local_service is None:
            self._local_service = await get_local_llm_service()
        return self._local_service

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion - Groq first, local fallback."""

        temp = temperature or 0.7
        max_tok = max_tokens or 2048

        # Try Groq first (primary)
        if GROQ_AVAILABLE and self.settings.groq_api_key:
            try:
                groq = await self._get_groq_service()
                if groq:
                    self._metrics["groq_requests"] += 1
                    logger.info("Using Groq API")

                    result = await groq.chat_completion(
                        messages=messages,
                        model=model,
                        temperature=temp,
                        max_tokens=max_tok,
                        stream=stream,
                        tools=tools,
                    )
                    if not result.get("success"):
                        raise RuntimeError(result.get("error", "Groq request failed"))
                    result["source"] = "groq"
                    result["provider"] = "groq"
                    return result
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
                if self.mode == "groq":
                    raise
                self._metrics["fallback_count"] += 1

        # Fallback to local LLM
        if LOCAL_AVAILABLE and self.mode in ("local", "auto"):
            try:
                local = await self._get_local_service()
                if local and local.is_available:
                    self._metrics["local_requests"] += 1
                    logger.info(f"Using local LLM ({local.provider})")

                    result = await local.generate(
                        messages=messages,
                        model=model,
                        temperature=temp,
                        max_tokens=max_tok,
                        stream=stream,
                    )
                    result["source"] = "local"
                    result["provider"] = local.provider
                    return result
            except Exception as e:
                logger.error(f"Local LLM also failed: {e}")
                self._metrics["errors"] += 1

        raise RuntimeError(
            "No AI provider available. "
            "Please set GROQ_API_KEY environment variable or install Ollama."
        )

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        temp = temperature or 0.7
        max_tok = max_tokens or 2048

        # Try Groq streaming first
        if GROQ_AVAILABLE and self.settings.groq_api_key:
            try:
                groq = await self._get_groq_service()
                if groq:
                    self._metrics["groq_requests"] += 1
                    # Note: Groq streaming implementation depends on groq_service
                    result = await groq.chat_completion(
                        messages=messages,
                        model=model,
                        temperature=temp,
                        max_tokens=max_tok,
                        stream=False,
                    )
                    yield result.get("content", "")
                    return
            except Exception as e:
                logger.warning(f"Groq streaming failed: {e}")

        # Fallback: return complete response
        result = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temp,
            max_tokens=max_tok,
            stream=False,
        )
        yield result.get("content", "")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models."""
        models = []

        # Groq models (always available if key is set)
        if GROQ_AVAILABLE and self.settings.groq_api_key:
            models.extend([
                {
                    "id": "llama-3.1-70b-versatile",
                    "name": "Llama 3.1 70B (Groq)",
                    "provider": "groq",
                    "provider_name": "groq",
                    "size": "~40GB",
                    "parameters": "70B",
                    "speed": "Very Fast (cloud)",
                    "capabilities": ["advanced_reasoning", "coding", "analysis", "multilingual"],
                    "best_for": ["complex_tasks", "production", "coding"],
                    "ram_required_mb": 0,
                },
                {
                    "id": "llama-3.1-8b-instant",
                    "name": "Llama 3.1 8B (Groq)",
                    "provider": "groq",
                    "provider_name": "groq",
                    "size": "~5GB",
                    "parameters": "8B",
                    "speed": "Ultra Fast (cloud)",
                    "capabilities": ["fast_inference", "chat", "basic_coding"],
                    "best_for": ["quick_responses", "chatbots", "simple_tasks"],
                    "ram_required_mb": 0,
                },
                {
                    "id": "mixtral-8x7b-32768",
                    "name": "Mixtral 8x7B (Groq)",
                    "provider": "groq",
                    "provider_name": "groq",
                    "size": "~47GB",
                    "parameters": "47B",
                    "speed": "Fast (cloud)",
                    "capabilities": ["reasoning", "multilingual", "coding"],
                    "best_for": ["complex_tasks", "multilingual"],
                    "ram_required_mb": 0,
                },
                {
                    "id": "gemma2-9b-it",
                    "name": "Gemma 2 9B (Groq)",
                    "provider": "groq",
                    "provider_name": "groq",
                    "size": "~6GB",
                    "parameters": "9B",
                    "speed": "Fast (cloud)",
                    "capabilities": ["reasoning", "safety", "instruction_following"],
                    "best_for": ["safe_content", "education"],
                    "ram_required_mb": 0,
                },
            ])

        # Local models (if available)
        if LOCAL_AVAILABLE:
            try:
                local = await self._get_local_service()
                if local and local.is_available:
                    for model_name in local.available_models:
                        info = local.get_model_info(model_name)
                        models.append({
                            "id": model_name,
                            "name": info["name"],
                            "provider": "local",
                            "provider_name": local.provider,
                            "size": info["size"],
                            "parameters": info["parameters"],
                            "speed": info["speed"],
                            "capabilities": info["capabilities"],
                            "best_for": info["best_for"],
                            "ram_required_mb": info["ram_required_mb"],
                        })
            except Exception as e:
                logger.debug(f"Could not get local models: {e}")

        return models

    async def pull_local_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model to local Ollama."""
        if not LOCAL_AVAILABLE:
            return {"error": "Local LLM not available"}
        local = await self._get_local_service()
        return await local.pull_model(model_name)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all AI providers."""
        groq_health = {"available": False}
        if GROQ_AVAILABLE and self.settings.groq_api_key:
            try:
                groq = await self._get_groq_service()
                groq_health = {"available": True, "key_configured": True}
            except Exception as e:
                groq_health = {"available": False, "error": str(e)}

        local_health = {"status": "not_configured"}
        if LOCAL_AVAILABLE:
            try:
                local = await self._get_local_service()
                local_health = await local.health_check()
            except Exception as e:
                local_health = {"status": "unavailable", "error": str(e)}

        return {
            "status": "healthy" if groq_health["available"] else ("degraded" if local_health.get("status") == "healthy" else "unavailable"),
            "mode": self.mode,
            "groq": groq_health,
            "local": local_health,
            "metrics": self._metrics,
        }

    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.copy()


_unified_service = None


async def get_unified_ai_service():
    global _unified_service
    if _unified_service is None:
        _unified_service = UnifiedAIService()
    return _unified_service
