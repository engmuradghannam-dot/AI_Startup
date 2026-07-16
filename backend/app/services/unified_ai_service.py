"""Unified AI Service - Multi-Provider Cloud Primary + Local LLM Optional.

Primary: whichever provider is active in Settings (falls back to that
provider's env var API key), across all 11 supported providers
Optional: Local LLM (Ollama/LocalAI) for local development
Auto mode: uses the configured cloud provider by default, tries local if configured
"""
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator

from app.config import get_settings
from app.services.multi_provider_ai import get_multi_provider_service

# Local LLM is optional
try:
    from app.services.local_llm_service import get_local_llm_service, LocalLLMService
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedAIService:
    """Unified AI service - delegates to whichever provider is configured (Settings or env var), local LLM as fallback."""

    def __init__(self):
        self.settings = get_settings()
        self.mode = self.settings.llm_mode
        self._local_service = None
        self._metrics = {
            "cloud_requests": 0,
            "local_requests": 0,
            "fallback_count": 0,
            "errors": 0,
        }

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
        """Generate chat completion - configured cloud provider first, local fallback."""

        temp = temperature or 0.7
        max_tok = max_tokens or 2048

        # Try the configured cloud provider first (Settings-configured or env var)
        try:
            multi = await get_multi_provider_service()
            result = await multi.chat_completion(
                messages=messages,
                model=model,
                temperature=temp,
                max_tokens=max_tok,
                stream=stream,
            )
            if not result.get("success"):
                raise RuntimeError(result.get("error", "AI provider request failed"))
            self._metrics["cloud_requests"] += 1
            logger.info(f"Using {result.get('provider', 'cloud')} provider")
            result["source"] = result.get("provider", "cloud")
            return result
        except Exception as e:
            logger.warning(f"Cloud provider failed: {e}")
            if self.mode not in ("local", "auto"):
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
            "Please configure a provider in Settings (or set its API key env var) or install Ollama."
        )

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream completion events: {"delta": text}, then {"done": True, ...}, or {"error": msg}."""
        temp = temperature or 0.7
        max_tok = max_tokens or 2048

        multi = await get_multi_provider_service()
        got_any_delta = False
        async for event in multi.stream_chat_completion(messages=messages, model=model, temperature=temp, max_tokens=max_tok):
            if "delta" in event:
                got_any_delta = True
                self._metrics["cloud_requests"] += 1
            yield event
            if "error" in event and not got_any_delta:
                # cloud provider never even started responding - try local as a fallback
                if LOCAL_AVAILABLE and self.mode in ("local", "auto"):
                    try:
                        local = await self._get_local_service()
                        if local and local.is_available:
                            self._metrics["local_requests"] += 1
                            result = await local.generate(messages=messages, model=model, temperature=temp, max_tokens=max_tok, stream=False)
                            yield {"delta": result.get("content", "")}
                            yield {"done": True, "model": result.get("model"), "provider": local.provider, "usage": {}}
                    except Exception as e:
                        self._metrics["errors"] += 1
                        logger.error(f"Local LLM fallback also failed: {e}")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models."""
        models = []

        try:
            multi = await get_multi_provider_service()
            for provider_id, config in multi.PROVIDERS.items():
                api_key = multi._get_api_key(provider_id)
                if not api_key:
                    continue
                for model_id in config.get("models", []):
                    models.append({
                        "id": model_id,
                        "name": f"{model_id} ({config['name']})",
                        "provider": provider_id,
                        "provider_name": config["name"],
                        "size": "unknown",
                        "parameters": "unknown",
                        "speed": "cloud",
                        "capabilities": ["chat"],
                        "best_for": ["general"],
                        "ram_required_mb": 0,
                    })
        except Exception as e:
            logger.debug(f"Could not get cloud provider models: {e}")

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
        cloud_health = {"available": False}
        try:
            multi = await get_multi_provider_service()
            active_provider = await multi._get_active_provider()
            if active_provider and active_provider != "ollama":
                cloud_health = {"available": True, "provider": active_provider, "key_configured": True}
        except Exception as e:
            cloud_health = {"available": False, "error": str(e)}

        local_health = {"status": "not_configured"}
        if LOCAL_AVAILABLE:
            try:
                local = await self._get_local_service()
                local_health = await local.health_check()
            except Exception as e:
                local_health = {"status": "unavailable", "error": str(e)}

        return {
            "status": "healthy" if cloud_health["available"] else ("degraded" if local_health.get("status") == "healthy" else "unavailable"),
            "mode": self.mode,
            "cloud": cloud_health,
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
