"""Load balancer for distributing tasks across agents."""
import random
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.agent import Agent, AgentStatus
from app.models.task import Task, TaskStatus


class LoadBalancer:
    """Service for load balancing tasks across agents."""

    def __init__(self):
        self._strategy = "weighted_round_robin"
        self._agent_queue: List[str] = []
        self._last_index = 0

    async def get_best_agent(
        self,
        required_capabilities: List[str],
        required_skills: List[str],
        priority: int = 3,
    ) -> Optional[Agent]:
        """Get the best agent for a task using load balancing."""

        # Find eligible agents
        eligible = await Agent.find(
            Agent.status == AgentStatus.IDLE,
        ).to_list()

        if not eligible:
            return None

        # Filter by capabilities
        if required_capabilities:
            eligible = [
                a for a in eligible
                if any(cap.name in required_capabilities for cap in a.capabilities)
            ]

        if not eligible:
            return None

        # Apply load balancing strategy
        if self._strategy == "weighted_round_robin":
            return await self._weighted_round_robin(eligible)
        elif self._strategy == "least_connections":
            return await self._least_connections(eligible)
        elif self._strategy == "random":
            return random.choice(eligible)
        else:
            return eligible[0]

    async def _weighted_round_robin(self, agents: List[Agent]) -> Agent:
        """Weighted round-robin selection."""
        # Sort by priority (higher first) and then round-robin
        sorted_agents = sorted(agents, key=lambda a: (-a.priority, a.metrics.last_active or datetime.min))

        self._last_index = (self._last_index + 1) % len(sorted_agents)
        return sorted_agents[self._last_index]

    async def _least_connections(self, agents: List[Agent]) -> Agent:
        """Select agent with least active tasks."""
        return min(agents, key=lambda a: a.metrics.tasks_completed + a.metrics.tasks_failed)

    async def distribute_batch(
        self,
        tasks: List[Task],
        strategy: str = "parallel",
    ) -> Dict[str, List[str]]:
        """Distribute a batch of tasks across agents."""

        distribution: Dict[str, List[str]] = {}

        if strategy == "parallel":
            # Assign each task to best available agent
            for task in tasks:
                agent = await self.get_best_agent(
                    task.required_capabilities,
                    task.required_skills,
                )
                if agent:
                    agent_id = str(agent.id)
                    if agent_id not in distribution:
                        distribution[agent_id] = []
                    distribution[agent_id].append(str(task.id))

                    # Mark agent as busy
                    agent.status = AgentStatus.BUSY
                    await agent.save()

        elif strategy == "round_robin":
            # Distribute evenly
            available = await Agent.find(Agent.status == AgentStatus.IDLE).to_list()
            if not available:
                return distribution

            for i, task in enumerate(tasks):
                agent = available[i % len(available)]
                agent_id = str(agent.id)
                if agent_id not in distribution:
                    distribution[agent_id] = []
                distribution[agent_id].append(str(task.id))

        return distribution

    async def get_load_metrics(self) -> Dict[str, Any]:
        """Get current load distribution metrics."""
        total = await Agent.find().count()
        idle = await Agent.find(Agent.status == AgentStatus.IDLE).count()
        busy = await Agent.find(Agent.status == AgentStatus.BUSY).count()

        # Get task queue
        pending_tasks = await Task.find(Task.status == TaskStatus.PENDING).count()
        running_tasks = await Task.find(Task.status == TaskStatus.RUNNING).count()

        return {
            "total_agents": total,
            "idle_agents": idle,
            "busy_agents": busy,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "load_factor": round(busy / total, 2) if total > 0 else 0,
            "queue_depth": pending_tasks,
            "strategy": self._strategy,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton
_load_balancer: Optional[LoadBalancer] = None


async def get_load_balancer() -> LoadBalancer:
    """Get or create load balancer."""
    global _load_balancer
    if _load_balancer is None:
        _load_balancer = LoadBalancer()
    return _load_balancer
