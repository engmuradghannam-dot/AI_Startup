"""Error recovery and self-healing service."""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.agent import Agent, AgentStatus
from app.models.task import Task, TaskStatus
from app.services.groq_service import get_groq_service


class ErrorRecovery:
    """Service for automatic error recovery and self-healing."""

    def __init__(self):
        self._recovery_strategies: Dict[str, Any] = {}
        self._recovery_history: List[Dict] = []
        self._max_retries = 3

    async def handle_task_failure(
        self,
        task: Task,
        agent: Agent,
        error: str,
    ) -> Dict[str, Any]:
        """Handle a failed task with recovery strategies."""

        if task.retry_count >= self._max_retries:
            return {
                "success": False,
                "action": "max_retries_exceeded",
                "message": f"Task failed after {self._max_retries} retries",
            }

        # Analyze error
        error_type = self._classify_error(error)

        # Apply recovery strategy
        if error_type == "timeout":
            result = await self._recover_timeout(task, agent)
        elif error_type == "rate_limit":
            result = await self._recover_rate_limit(task, agent)
        elif error_type == "context_length":
            result = await self._recover_context_length(task, agent)
        elif error_type == "api_error":
            result = await self._recover_api_error(task, agent)
        else:
            result = await self._recover_generic(task, agent, error)

        # Update retry count
        task.retry_count += 1
        task.status = TaskStatus.RETRYING
        await task.save()

        self._recovery_history.append({
            "task_id": str(task.id),
            "agent_id": str(agent.id),
            "error_type": error_type,
            "action": result.get("action"),
            "success": result.get("success"),
            "timestamp": datetime.utcnow().isoformat(),
        })

        return result

    def _classify_error(self, error: str) -> str:
        """Classify error type."""
        error_lower = error.lower()

        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        elif "rate limit" in error_lower or "429" in error_lower:
            return "rate_limit"
        elif "context length" in error_lower or "too long" in error_lower:
            return "context_length"
        elif "api" in error_lower or "500" in error_lower or "502" in error_lower:
            return "api_error"
        else:
            return "unknown"

    async def _recover_timeout(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Recover from timeout by increasing timeout and retrying."""
        # Increase timeout
        task.config["timeout"] = task.config.get("timeout", 300) * 2

        # Try with a different model if available
        agent.model = "mixtral-8x7b-32768"  # Faster model
        await agent.save()

        return {
            "success": True,
            "action": "increased_timeout_and_switched_model",
            "new_timeout": task.config["timeout"],
            "new_model": agent.model,
        }

    async def _recover_rate_limit(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Recover from rate limit by waiting and retrying."""
        # Wait before retry
        await asyncio.sleep(5 * (task.retry_count + 1))

        return {
            "success": True,
            "action": "waited_and_retried",
            "wait_seconds": 5 * (task.retry_count + 1),
        }

    async def _recover_context_length(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Recover from context length error by summarizing."""
        # Summarize context
        groq = await get_groq_service()

        messages = [
            {"role": "system", "content": "Summarize the following context concisely:"},
            {"role": "user", "content": str(task.context)[:8000]},
        ]

        result = await groq.chat_completion(messages=messages, max_tokens=2000)

        if result["success"]:
            task.context = {"summary": result["content"]}
            await task.save()

            return {
                "success": True,
                "action": "summarized_context",
                "original_length": len(str(task.context)),
            }

        return {
            "success": False,
            "action": "failed_to_summarize",
            "error": result.get("error"),
        }

    async def _recover_api_error(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Recover from API error."""
        # Wait and retry
        await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff

        return {
            "success": True,
            "action": "exponential_backoff_retry",
            "wait_seconds": 2 ** task.retry_count,
        }

    async def _recover_generic(self, task: Task, agent: Agent, error: str) -> Dict[str, Any]:
        """Generic recovery - try with modified parameters."""
        # Reduce temperature for more deterministic output
        agent.temperature = max(0.1, agent.temperature - 0.1)
        await agent.save()

        return {
            "success": True,
            "action": "adjusted_parameters",
            "new_temperature": agent.temperature,
        }

    async def self_heal_agent(self, agent: Agent) -> Dict[str, Any]:
        """Attempt to self-heal a problematic agent."""

        # Reset agent state
        agent.status = AgentStatus.IDLE
        agent.metrics.tasks_failed = 0
        agent.temperature = 0.7
        agent.model = "llama-3.3-70b-versatile"

        # Clear short-term memory
        agent.memory.short_term = []

        await agent.save()

        return {
            "success": True,
            "action": "agent_reset",
            "agent_id": str(agent.id),
            "message": "Agent has been reset to default state",
        }

    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        total = len(self._recovery_history)
        successful = sum(1 for r in self._recovery_history if r.get("success"))

        error_types = {}
        for r in self._recovery_history:
            et = r.get("error_type", "unknown")
            error_types[et] = error_types.get(et, 0) + 1

        return {
            "total_recoveries": total,
            "successful_recoveries": successful,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
            "error_type_distribution": error_types,
            "recent_recoveries": self._recovery_history[-10:],
        }


# Singleton
_error_recovery: Optional[ErrorRecovery] = None


async def get_error_recovery() -> ErrorRecovery:
    """Get or create error recovery service."""
    global _error_recovery
    if _error_recovery is None:
        _error_recovery = ErrorRecovery()
    return _error_recovery
