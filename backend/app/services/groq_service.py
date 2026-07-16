"""Groq API integration service."""
import asyncio
import httpx
import json
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime

from app.config import get_settings


class GroqService:
    """Service for interacting with Groq API."""

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(
            base_url=self.settings.groq_base_url,
            headers={
                "Authorization": f"Bearer {self.settings.groq_api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )
        self._request_count = 0
        self._token_count = 0
        self._cost_estimate = 0.0


    async def validate_api_key(self) -> Dict[str, Any]:
        """Validate the Groq API key by fetching available models."""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            models = response.json()
            return {
                "valid": True,
                "models_count": len(models.get("data", [])),
                "message": "API key is valid",
            }
        except httpx.HTTPStatusError as e:
            return {
                "valid": False,
                "status_code": e.response.status_code,
                "message": f"API key validation failed: {e.response.status_code}",
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"API key validation error: {str(e)}",
            }
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Send chat completion request to Groq."""

        payload = {
            "model": model or self.settings.groq_default_model,
            "messages": messages,
            "temperature": temperature or self.settings.groq_temperature,
            "max_tokens": max_tokens or self.settings.groq_max_tokens,
            "stream": stream,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        start_time = time.time()

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()

            # Update metrics
            self._request_count += 1
            usage = data.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            self._token_count += tokens

            # Estimate cost (approximate)
            cost = tokens * 0.00001  # $0.01 per 1K tokens
            self._cost_estimate += cost

            execution_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "content": data["choices"][0]["message"]["content"],
                "tool_calls": data["choices"][0]["message"].get("tool_calls", []),
                "usage": usage,
                "cost_usd": cost,
                "execution_time_ms": execution_time,
                "model": data.get("model", model),
                "raw_response": data,
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            if e.response.status_code == 401:
                error_msg = "Invalid Groq API key. Please check your GROQ_API_KEY environment variable."
            elif e.response.status_code == 405:
                error_msg = "Method Not Allowed. The Groq API endpoint or model may not be available."
            elif e.response.status_code == 429:
                error_msg = "Rate limit exceeded. Please wait a moment and try again."
            return {
                "success": False,
                "error": error_msg,
                "execution_time_ms": (time.time() - start_time) * 1000,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000,
            }

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion from Groq."""

        payload = {
            "model": model or self.settings.groq_default_model,
            "messages": messages,
            "temperature": temperature or self.settings.groq_temperature,
            "max_tokens": max_tokens or self.settings.groq_max_tokens,
            "stream": True,
        }

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        content = chunk["choices"][0]["delta"].get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue

    async def batch_chat(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 10,
    ) -> List[Dict[str, Any]]:
        """Execute multiple chat requests in parallel."""

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _execute(req):
            async with semaphore:
                return await self.chat_completion(**req)

        tasks = [_execute(req) for req in requests]
        return await asyncio.gather(*tasks)

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            "total_requests": self._request_count,
            "total_tokens": self._token_count,
            "estimated_cost_usd": round(self._cost_estimate, 4),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Singleton instance
_groq_service: Optional[GroqService] = None


async def get_groq_service() -> GroqService:
    """Get or create Groq service instance."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
