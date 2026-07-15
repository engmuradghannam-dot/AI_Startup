"""Unified AI Service - Combines Groq + Local LLM with intelligent fallback.

Primary: Local LLM (Ollama/LocalAI) - FREE, no API keys
Fallback: Groq API (if configured)
Auto mode: Tries local first, falls back to Groq if unavailable
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.config import get_settings
from app.services.local_llm_service import get_local_llm_service, LocalLLMService

try:
    from app.services.groq_service import get_groq_service
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedAIService:
    """Unified AI service with local-first architecture."""

    def __init__(self):
        self.settings = get_settings()
        self.mode = self.settings.llm_mode
        self._local_service: Optional[LocalLLMService] = None
        self._groq_service = None
        self._metrics = {
            "local_requests": 0,
            "groq_requests": 0,
            "fallback_count": 0,
            "errors": 0,
        }

    async def _get_local_service(self) -> LocalLLMService:
        if self._local_service is None:
            self._local_service = await get_local_llm_service()
        return self._local_service

    async def _get_groq_service(self):
        if not GROQ_AVAILABLE:
            return None
        if self._groq_service is None:
            self._groq_service = await get_groq_service()
        return self._groq_service

    def _should_use_local(self) -> bool:
        if self.mode == "local":
            return True
        if self.mode == "groq":
            return False
        return True

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion with automatic fallback."""

        temp = temperature or 0.7
        max_tok = max_tokens or 2048

        if self._should_use_local():
            try:
                local = await self._get_local_service()
                if local.is_available:
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
                logger.warning(f"Local LLM failed: {e}")
                if self.mode == "local":
                    raise
                self._metrics["fallback_count"] += 1

        if GROQ_AVAILABLE and self.settings.groq_api_key:
            try:
                groq = await self._get_groq_service()
                if groq:
                    self._metrics["groq_requests"] += 1
                    logger.info("Using Groq API (fallback)")

                    result = await groq.chat_completion(
                        messages=messages,
                        model=model,
                        temperature=temp,
                        max_tokens=max_tok,
                        stream=stream,
                        tools=tools,
                    )
                    result["source"] = "groq"
                    return result
            except Exception as e:
                logger.error(f"Groq also failed: {e}")
                self._metrics["errors"] += 1
                raise RuntimeError(f"All AI providers failed. Local: unavailable, Groq: {e}")

        raise RuntimeError(
            "No AI provider available. "
            "Please install Ollama (https://ollama.com) or configure GROQ_API_KEY"
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

        if self._should_use_local():
            try:
                local = await self._get_local_service()
                if local.is_available:
                    self._metrics["local_requests"] += 1
                    async for token in local.stream_generate(
                        messages=messages,
                        model=model,
                        temperature=temp,
                        max_tokens=max_tok,
                    ):
                        yield token
                    return
            except Exception as e:
                logger.warning(f"Local streaming failed: {e}")
                if self.mode == "local":
                    raise

        result = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temp,
            max_tokens=max_tok,
            stream=False,
        )
        yield result.get("content", "")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models from all providers."""
        models = []

        try:
            local = await self._get_local_service()
            if local.is_available:
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

        if GROQ_AVAILABLE and self.settings.groq_api_key:
            models.append({
                "id": "llama-3.1-70b-versatile",
                "name": "Llama 3.1 70B (Groq)",
                "provider": "groq",
                "provider_name": "groq",
                "size": "~40GB",
                "parameters": "70B",
                "speed": "Very Fast (cloud)",
                "capabilities": ["advanced_reasoning", "coding", "analysis"],
                "best_for": ["complex_tasks", "production"],
                "ram_required_mb": 0,
            })

        return models

    async def pull_local_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model to local Ollama."""
        local = await self._get_local_service()
        return await local.pull_model(model_name)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all AI providers."""
        local = await self._get_local_service()
        local_health = await local.health_check()

        groq_health = {"available": False}
        if GROQ_AVAILABLE and self.settings.groq_api_key:
            try:
                groq = await self._get_groq_service()
                groq_health = {"available": True, "key_configured": True}
            except:
                pass

        return {
            "status": "healthy" if (local_health["status"] == "healthy" or groq_health["available"]) else "degraded",
            "mode": self.mode,
            "local": local_health,
            "groq": groq_health,
            "metrics": self._metrics,
        }

    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.copy()


_unified_service: Optional[UnifiedAIService] = None


async def get_unified_ai_service() -> UnifiedAIService:
    global _unified_service
    if _unified_service is None:
        _unified_service = UnifiedAIService()
    return _unified_service
