"""Local LLM Service - Ollama & LocalAI Integration.

This service provides a unified interface for local LLM inference
without requiring any external API keys. Supports Ollama and LocalAI.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Available local models with their specs
AVAILABLE_MODELS = {
    "qwen3:0.6b": {
        "name": "Qwen3 0.6B",
        "size": "~500MB",
        "parameters": "0.6B",
        "speed": "Very Fast (~34 tok/s)",
        "capabilities": ["fast_inference", "basic_reasoning", "code"],
        "best_for": ["quick_responses", "simple_tasks", "high_throughput"],
        "ram_required_mb": 1024,
    },
    "tinyllama": {
        "name": "TinyLlama 1.1B",
        "size": "~638MB",
        "parameters": "1.1B",
        "speed": "Fast (~25 tok/s)",
        "capabilities": ["coding", "chat", "summarization"],
        "best_for": ["coding_assistance", "chatbots", "education"],
        "ram_required_mb": 1536,
    },
    "gemma3:1b": {
        "name": "Gemma 3 1B",
        "size": "~815MB",
        "parameters": "1B",
        "speed": "Fast (~18 tok/s)",
        "capabilities": ["reasoning", "safety", "multilingual"],
        "best_for": ["safe_content", "multilingual", "structured_output"],
        "ram_required_mb": 1536,
    },
    "phi4-mini": {
        "name": "Phi-4 Mini 3.8B",
        "size": "~2.5GB",
        "parameters": "3.8B",
        "speed": "Moderate (~7 tok/s)",
        "capabilities": ["reasoning", "coding", "math", "instruction_following"],
        "best_for": ["complex_reasoning", "agent_tasks", "detailed_analysis"],
        "ram_required_mb": 4096,
    },
    "llama3.2:1b": {
        "name": "Llama 3.2 1B",
        "size": "~1.3GB",
        "parameters": "1B",
        "speed": "Fast (~20 tok/s)",
        "capabilities": ["general", "chat", "multilingual"],
        "best_for": ["general_tasks", "chat", "lightweight"],
        "ram_required_mb": 2048,
    },
}


class LocalLLMService:
    """Unified service for local LLM inference via Ollama or LocalAI."""

    def __init__(self):
        self.settings = get_settings()
        self.ollama_host = self.settings.ollama_host
        self.localai_host = self.settings.localai_host
        self.default_model = self.settings.ollama_default_model
        self.fallback_model = self.settings.ollama_fallback_model
        self._available_models: List[str] = []
        self._provider: Optional[str] = None
        self._client = httpx.AsyncClient(timeout=120.0)

    async def _check_ollama(self) -> bool:
        """Check if Ollama is running and get available models."""
        try:
            response = await self._client.get(
                f"{self.ollama_host}/api/tags",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                self._available_models = [m["name"] for m in data.get("models", [])]
                self._provider = "ollama"
                logger.info(f"Ollama connected. Models: {self._available_models}")
                return True
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        return False

    async def _check_localai(self) -> bool:
        """Check if LocalAI is running."""
        try:
            response = await self._client.get(
                f"{self.localai_host}/models",
                timeout=5.0
            )
            if response.status_code == 200:
                self._provider = "localai"
                logger.info("LocalAI connected")
                return True
        except Exception as e:
            logger.debug(f"LocalAI not available: {e}")
        return False

    async def initialize(self) -> bool:
        """Initialize and detect available local LLM provider."""
        if await self._check_ollama():
            return True
        if await self._check_localai():
            return True
        logger.warning("No local LLM provider available")
        return False

    @property
    def is_available(self) -> bool:
        """Check if a local provider is configured."""
        return self._provider is not None

    @property
    def provider(self) -> Optional[str]:
        """Get current provider name."""
        return self._provider

    @property
    def available_models(self) -> List[str]:
        """Get list of available model names."""
        return self._available_models

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if model_name in AVAILABLE_MODELS:
            return AVAILABLE_MODELS[model_name]
        for key, info in AVAILABLE_MODELS.items():
            if key in model_name or model_name in key:
                return info
        return {
            "name": model_name,
            "size": "Unknown",
            "parameters": "Unknown",
            "speed": "Unknown",
            "capabilities": [],
            "best_for": [],
            "ram_required_mb": 2048,
        }

    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model from Ollama registry."""
        if self._provider != "ollama":
            return {"error": "Model pulling only supported with Ollama"}

        try:
            response = await self._client.post(
                f"{self.ollama_host}/api/pull",
                json={"name": model_name, "stream": False},
                timeout=300.0
            )
            if response.status_code == 200:
                await self._check_ollama()
                return {"status": "success", "model": model_name}
            return {"error": f"Failed to pull model: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Generate completion using local LLM."""
        model = model or self.default_model

        if not self._provider:
            if not await self.initialize():
                raise RuntimeError("No local LLM provider available")

        if self._provider == "ollama":
            return await self._ollama_generate(messages, model, temperature, max_tokens, stream)
        elif self._provider == "localai":
            return await self._localai_generate(messages, model, temperature, max_tokens, stream)
        else:
            raise RuntimeError("Unknown provider")

    async def _ollama_generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate using Ollama API."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = await self._client.post(
                f"{self.ollama_host}/api/chat",
                json=payload,
                timeout=120.0
            )

            if response.status_code != 200:
                if model != self.fallback_model:
                    logger.info(f"Trying fallback model: {self.fallback_model}")
                    payload["model"] = self.fallback_model
                    response = await self._client.post(
                        f"{self.ollama_host}/api/chat",
                        json=payload,
                        timeout=120.0
                    )
                else:
                    raise RuntimeError(f"LLM generation failed: {response.status_code}")

            if stream:
                return {"stream": response}

            data = response.json()
            content = data.get("message", {}).get("content", "")

            return {
                "content": content,
                "model": model,
                "provider": "ollama",
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

        except httpx.TimeoutException:
            raise RuntimeError("Local LLM request timed out. Model may be loading.")
        except Exception as e:
            raise RuntimeError(f"Local LLM error: {str(e)}")

    async def _localai_generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> Dict[str, Any]:
        """Generate using LocalAI OpenAI-compatible API."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            response = await self._client.post(
                f"{self.localai_host}/v1/chat/completions",
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "content": data["choices"][0]["message"]["content"],
                "model": model,
                "provider": "localai",
                "usage": data.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise RuntimeError(f"LocalAI error: {str(e)}")

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream generation tokens."""
        model = model or self.default_model

        if self._provider == "ollama":
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            async with self._client.stream(
                "POST",
                f"{self.ollama_host}/api/chat",
                json=payload,
                timeout=120.0
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue

    async def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generate embeddings using local model."""
        model = model or "nomic-embed-text"

        if self._provider == "ollama":
            try:
                response = await self._client.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={"model": model, "prompt": text},
                    timeout=30.0
                )
                data = response.json()
                return data.get("embedding", [])
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                return []
        return []

    async def health_check(self) -> Dict[str, Any]:
        """Check local LLM health."""
        ollama_ok = await self._check_ollama()
        localai_ok = await self._check_localai()

        return {
            "status": "healthy" if (ollama_ok or localai_ok) else "unavailable",
            "ollama": {"connected": ollama_ok, "host": self.ollama_host},
            "localai": {"connected": localai_ok, "host": self.localai_host},
            "provider": self._provider,
            "available_models": self._available_models,
            "default_model": self.default_model,
            "fallback_model": self.fallback_model,
        }


# Singleton instance
_local_llm_service: Optional[LocalLLMService] = None


async def get_local_llm_service() -> LocalLLMService:
    """Get or create LocalLLMService singleton."""
    global _local_llm_service
    if _local_llm_service is None:
        _local_llm_service = LocalLLMService()
        await _local_llm_service.initialize()
    return _local_llm_service
