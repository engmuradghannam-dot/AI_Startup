"""Auto-scaling service for dynamic agent creation."""
import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.models.agent import Agent, AgentCreate, AgentStatus, AgentRole
from app.config import get_settings


class AutoScaler:
    """Service for auto-scaling agents based on workload."""

    def __init__(self):
        self.settings = get_settings()
        self._scale_groups: Dict[str, Dict[str, Any]] = {}
        self._scaling_history: List[Dict] = []
        self._is_running = False

    async def start_monitoring(self):
        """Start auto-scaling monitoring loop."""
        if self._is_running:
            return

        self._is_running = True
        while self._is_running:
            await self._evaluate_scaling()
            await asyncio.sleep(30)  # Check every 30 seconds

    def stop_monitoring(self):
        """Stop auto-scaling monitoring."""
        self._is_running = False

    async def _evaluate_scaling(self):
        """Evaluate and execute scaling decisions."""
        # Get current metrics
        total_agents = await Agent.find().count()
        busy_agents = await Agent.find(Agent.status == AgentStatus.BUSY).count()
        idle_agents = await Agent.find(Agent.status == AgentStatus.IDLE).count()

        utilization = busy_agents / total_agents if total_agents > 0 else 0

        # Scale up if utilization is high
        if utilization > 0.8 and total_agents < self.settings.auto_scale_max_agents:
            agents_to_add = min(
                max(1, int(total_agents * 0.2)),  # Add 20%
                self.settings.auto_scale_max_agents - total_agents
            )
            await self._scale_up(agents_to_add)

        # Scale down if too many idle agents
        elif utilization < 0.2 and idle_agents > self.settings.auto_scale_min_agents:
            agents_to_remove = min(
                idle_agents - self.settings.auto_scale_min_agents,
                int(idle_agents * 0.3)  # Remove 30% of idle
            )
            await self._scale_down(agents_to_remove)

    async def _scale_up(self, count: int, role: AgentRole = AgentRole.GENERAL):
        """Create new agents."""
        from app.services.agent_service import get_agent_service

        agent_service = await get_agent_service()
        created = []

        for i in range(count):
            agent_data = AgentCreate(
                name=f"AutoScaled-{role.value}-{uuid.uuid4().hex[:8]}",
                role=role,
                description=f"Auto-scaled agent for {role.value} tasks",
                priority=3,
            )
            agent = await agent_service.create_agent(agent_data)
            agent.is_auto_scaled = True
            agent.scale_group = "auto"
            await agent.save()
            created.append(agent)

        self._scaling_history.append({
            "action": "scale_up",
            "count": count,
            "role": role.value,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_ids": [str(a.id) for a in created],
        })

        return created

    async def _scale_down(self, count: int):
        """Remove idle auto-scaled agents."""
        agents = await Agent.find(
            Agent.status == AgentStatus.IDLE,
            Agent.is_auto_scaled == True,
        ).limit(count).to_list()

        removed = []
        for agent in agents:
            await agent.delete()
            removed.append(str(agent.id))

        self._scaling_history.append({
            "action": "scale_down",
            "count": len(removed),
            "timestamp": datetime.utcnow().isoformat(),
            "agent_ids": removed,
        })

        return removed

    async def scale_for_task(
        self,
        task_type: str,
        required_agents: int = 1,
    ) -> List[Agent]:
        """Scale up for a specific task type."""
        role_map = {
            "marketing": AgentRole.MARKETING,
            "legal": AgentRole.LEGAL,
            "finance": AgentRole.FINANCE,
            "hr": AgentRole.HR,
            "healthcare": AgentRole.HEALTHCARE,
            "development": AgentRole.DEVELOPER,
            "design": AgentRole.DESIGNER,
            "analysis": AgentRole.ANALYST,
            "security": AgentRole.SECURITY,
            "devops": AgentRole.DEVOPS,
        }

        role = role_map.get(task_type.lower(), AgentRole.GENERAL)

        # Check available agents
        available = await Agent.find(
            Agent.role == role,
            Agent.status == AgentStatus.IDLE,
        ).count()

        if available < required_agents:
            needed = required_agents - available
            return await self._scale_up(needed, role)

        return await Agent.find(
            Agent.role == role,
            Agent.status == AgentStatus.IDLE,
        ).limit(required_agents).to_list()

    def get_scaling_history(self, limit: int = 100) -> List[Dict]:
        """Get scaling history."""
        return self._scaling_history[-limit:]

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current scaling metrics."""
        total = await Agent.find().count()
        busy = await Agent.find(Agent.status == AgentStatus.BUSY).count()
        idle = await Agent.find(Agent.status == AgentStatus.IDLE).count()
        auto_scaled = await Agent.find(Agent.is_auto_scaled == True).count()

        return {
            "total_agents": total,
            "busy_agents": busy,
            "idle_agents": idle,
            "auto_scaled_agents": auto_scaled,
            "utilization_rate": round(busy / total * 100, 2) if total > 0 else 0,
            "auto_scaling_enabled": self.settings.auto_scale_enabled,
            "max_agents": self.settings.auto_scale_max_agents,
            "min_agents": self.settings.auto_scale_min_agents,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton
_auto_scaler: Optional[AutoScaler] = None


async def get_auto_scaler() -> AutoScaler:
    """Get or create auto-scaler."""
    global _auto_scaler
    if _auto_scaler is None:
        _auto_scaler = AutoScaler()
    return _auto_scaler
