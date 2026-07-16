"""Cost optimization service."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.models.agent import Agent
from app.config import get_settings


class CostOptimizer:
    """Service for optimizing API costs."""

    def __init__(self):
        self.settings = get_settings()
        self._daily_cost = 0.0
        self._cost_history: List[Dict] = []
        self._model_tiers = {
            "llama-3.3-70b-versatile": {"cost_per_1k": 0.59, "quality": "high", "speed": "fast"},
            "llama-3.1-8b-instant": {"cost_per_1k": 0.05, "quality": "medium", "speed": "fastest"},
            "mixtral-8x7b-32768": {"cost_per_1k": 0.24, "quality": "medium", "speed": "fast"},
            "gemma-7b-it": {"cost_per_1k": 0.07, "quality": "low", "speed": "fast"},
        }

    async def select_optimal_model(
        self,
        task_complexity: str = "medium",
        max_cost_usd: Optional[float] = None,
        required_quality: str = "medium",
    ) -> str:
        """Select the most cost-effective model for a task."""

        complexity_map = {
            "low": ["gemma-7b-it", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama-3.3-70b-versatile"],
            "medium": ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama-3.3-70b-versatile"],
            "high": ["mixtral-8x7b-32768", "llama-3.3-70b-versatile"],
            "critical": ["llama-3.3-70b-versatile"],
        }

        candidates = complexity_map.get(task_complexity, complexity_map["medium"])

        # Filter by budget
        if max_cost_usd:
            candidates = [
                m for m in candidates
                if self._model_tiers[m]["cost_per_1k"] <= max_cost_usd * 1000
            ]

        # Filter by quality requirement
        quality_map = {"low": ["low", "medium", "high"], "medium": ["medium", "high"], "high": ["high"]}
        allowed_quality = quality_map.get(required_quality, ["medium", "high"])
        candidates = [m for m in candidates if self._model_tiers[m]["quality"] in allowed_quality]

        if not candidates:
            return "llama-3.1-8b-instant"  # Default fallback

        # Select cheapest from remaining
        return min(candidates, key=lambda m: self._model_tiers[m]["cost_per_1k"])

    async def estimate_task_cost(
        self,
        prompt_tokens: int,
        expected_output_tokens: int,
        model: str,
    ) -> Dict[str, float]:
        """Estimate cost for a task."""

        tier = self._model_tiers.get(model, self._model_tiers["llama-3.3-70b-versatile"])
        cost_per_1k = tier["cost_per_1k"]

        input_cost = (prompt_tokens / 1000) * cost_per_1k
        output_cost = (expected_output_tokens / 1000) * cost_per_1k
        total_cost = input_cost + output_cost

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "model": model,
        }

    async def track_cost(self, agent_id: str, cost_usd: float, tokens: int):
        """Track cost usage."""
        self._daily_cost += cost_usd

        self._cost_history.append({
            "agent_id": agent_id,
            "cost_usd": cost_usd,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Check budget
        budget = self.settings.cost_budget_usd
        threshold = self.settings.cost_alert_threshold

        if self._daily_cost > budget * threshold:
            return {
                "alert": True,
                "message": f"Cost alert: ${self._daily_cost:.2f} / ${budget:.2f} ({self._daily_cost/budget*100:.1f}%)",
                "current_cost": self._daily_cost,
                "budget": budget,
                "percentage": self._daily_cost / budget * 100,
            }

        return {"alert": False, "current_cost": self._daily_cost}

    async def optimize_agent_config(self, agent: Agent) -> Dict[str, Any]:
        """Optimize agent configuration for cost."""

        # Check if agent is using expensive model unnecessarily
        if agent.model == "llama-3.3-70b-versatile" and agent.metrics.tasks_completed > 100:
            # Agent has experience, can use cheaper model
            agent.model = "llama-3.1-8b-instant"

        # Reduce max_tokens if agent consistently uses less
        avg_tokens = agent.metrics.total_tokens_used / max(agent.metrics.tasks_completed, 1)
        if avg_tokens < agent.max_tokens * 0.5:
            agent.max_tokens = int(avg_tokens * 1.2)  # 20% buffer

        await agent.save()

        return {
            "optimized": True,
            "new_model": agent.model,
            "new_max_tokens": agent.max_tokens,
            "estimated_savings": "20-40%",
        }

    def get_cost_report(self) -> Dict[str, Any]:
        """Get comprehensive cost report."""

        # Group by agent
        agent_costs = {}
        for entry in self._cost_history:
            aid = entry["agent_id"]
            if aid not in agent_costs:
                agent_costs[aid] = {"cost": 0, "tokens": 0}
            agent_costs[aid]["cost"] += entry["cost_usd"]
            agent_costs[aid]["tokens"] += entry["tokens"]

        # Sort by cost
        top_agents = sorted(
            [{"agent_id": k, **v} for k, v in agent_costs.items()],
            key=lambda x: x["cost"],
            reverse=True,
        )[:10]

        return {
            "daily_cost": round(self._daily_cost, 4),
            "budget": self.settings.cost_budget_usd,
            "budget_remaining": round(self.settings.cost_budget_usd - self._daily_cost, 4),
            "budget_percentage": round(self._daily_cost / self.settings.cost_budget_usd * 100, 2),
            "total_requests": len(self._cost_history),
            "top_consumers": top_agents,
            "model_costs": self._model_tiers,
        }


# Singleton
_cost_optimizer: Optional[CostOptimizer] = None


async def get_cost_optimizer() -> CostOptimizer:
    """Get or create cost optimizer."""
    global _cost_optimizer
    if _cost_optimizer is None:
        _cost_optimizer = CostOptimizer()
    return _cost_optimizer
