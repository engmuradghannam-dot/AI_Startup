"""Performance monitoring service."""
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque

from app.models.agent import Agent, AgentStatus
from app.models.task import Task, TaskStatus


class PerformanceMonitor:
    """Service for monitoring system performance."""

    def __init__(self):
        self._metrics_buffer: Dict[str, deque] = {
            "response_times": deque(maxlen=1000),
            "throughput": deque(maxlen=1000),
            "error_rates": deque(maxlen=1000),
            "agent_utilization": deque(maxlen=1000),
        }
        self._alerts: List[Dict] = []
        self._alert_thresholds = {
            "avg_response_time_ms": 5000,
            "error_rate": 0.1,
            "agent_utilization": 0.95,
        }

    async def record_task_completion(
        self,
        task: Task,
        agent: Agent,
    ):
        """Record task completion metrics."""

        self._metrics_buffer["response_times"].append({
            "value": task.execution_time_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": str(task.id),
            "agent_id": str(agent.id),
        })

        self._metrics_buffer["throughput"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": str(task.id),
        })

    async def record_error(
        self,
        task: Task,
        agent: Agent,
        error: str,
    ):
        """Record error metrics."""

        self._metrics_buffer["error_rates"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": str(task.id),
            "agent_id": str(agent.id),
            "error": error,
        })

    async def check_alerts(self) -> List[Dict]:
        """Check for performance alerts."""
        alerts = []

        # Check response time
        if self._metrics_buffer["response_times"]:
            avg_rt = sum(m["value"] for m in self._metrics_buffer["response_times"]) / len(self._metrics_buffer["response_times"])
            if avg_rt > self._alert_thresholds["avg_response_time_ms"]:
                alerts.append({
                    "type": "high_response_time",
                    "severity": "warning",
                    "message": f"Average response time is {avg_rt:.0f}ms (threshold: {self._alert_thresholds['avg_response_time_ms']}ms)",
                    "value": avg_rt,
                    "threshold": self._alert_thresholds["avg_response_time_ms"],
                    "timestamp": datetime.utcnow().isoformat(),
                })

        # Check error rate
        if self._metrics_buffer["error_rates"]:
            total_tasks = len(self._metrics_buffer["throughput"])
            error_count = len(self._metrics_buffer["error_rates"])
            error_rate = error_count / total_tasks if total_tasks > 0 else 0

            if error_rate > self._alert_thresholds["error_rate"]:
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "critical",
                    "message": f"Error rate is {error_rate*100:.1f}% (threshold: {self._alert_thresholds['error_rate']*100:.0f}%)",
                    "value": error_rate,
                    "threshold": self._alert_thresholds["error_rate"],
                    "timestamp": datetime.utcnow().isoformat(),
                })

        # Check agent utilization
        total_agents = await Agent.find().count()
        busy_agents = await Agent.find(Agent.status == AgentStatus.BUSY).count()
        utilization = busy_agents / total_agents if total_agents > 0 else 0

        if utilization > self._alert_thresholds["agent_utilization"]:
            alerts.append({
                "type": "high_utilization",
                "severity": "warning",
                "message": f"Agent utilization is {utilization*100:.1f}% (threshold: {self._alert_thresholds['agent_utilization']*100:.0f}%)",
                "value": utilization,
                "threshold": self._alert_thresholds["agent_utilization"],
                "timestamp": datetime.utcnow().isoformat(),
            })

        self._alerts.extend(alerts)
        return alerts

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get metrics for dashboard."""

        # Calculate averages
        avg_response_time = 0
        if self._metrics_buffer["response_times"]:
            avg_response_time = sum(m["value"] for m in self._metrics_buffer["response_times"]) / len(self._metrics_buffer["response_times"])

        # Calculate throughput (tasks per minute)
        throughput = 0
        if len(self._metrics_buffer["throughput"]) >= 2:
            first = datetime.fromisoformat(self._metrics_buffer["throughput"][0]["timestamp"])
            last = datetime.fromisoformat(self._metrics_buffer["throughput"][-1]["timestamp"])
            duration_minutes = (last - first).total_seconds() / 60
            if duration_minutes > 0:
                throughput = len(self._metrics_buffer["throughput"]) / duration_minutes

        # Error rate
        total_tasks = len(self._metrics_buffer["throughput"])
        error_count = len(self._metrics_buffer["error_rates"])
        error_rate = error_count / total_tasks if total_tasks > 0 else 0

        # Agent stats
        total_agents = await Agent.find().count()
        idle_agents = await Agent.find(Agent.status == AgentStatus.IDLE).count()
        busy_agents = await Agent.find(Agent.status == AgentStatus.BUSY).count()

        return {
            "performance": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "throughput_per_minute": round(throughput, 2),
                "error_rate": round(error_rate, 4),
                "success_rate": round(1 - error_rate, 4),
            },
            "agents": {
                "total": total_agents,
                "idle": idle_agents,
                "busy": busy_agents,
                "utilization": round(busy_agents / total_agents, 4) if total_agents > 0 else 0,
            },
            "tasks": {
                "completed": await Task.find(Task.status == TaskStatus.COMPLETED).count(),
                "failed": await Task.find(Task.status == TaskStatus.FAILED).count(),
                "pending": await Task.find(Task.status == TaskStatus.PENDING).count(),
                "running": await Task.find(Task.status == TaskStatus.RUNNING).count(),
            },
            "alerts": self._alerts[-10:],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_historical_metrics(
        self,
        metric_type: str,
        hours: int = 24,
    ) -> List[Dict]:
        """Get historical metrics."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        buffer = self._metrics_buffer.get(metric_type, deque())
        return [
            m for m in buffer
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]


# Singleton
_performance_monitor: Optional[PerformanceMonitor] = None


async def get_performance_monitor() -> PerformanceMonitor:
    """Get or create performance monitor."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
