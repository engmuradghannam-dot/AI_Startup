"""Notification and Monitoring System.

Provides real-time monitoring, alerts, and notifications
for the AI Startup platform.
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from collections import defaultdict
from enum import Enum
import uuid


class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    SYSTEM = "system"
    AGENT = "agent"
    TASK = "task"
    ALERT = "alert"
    PERFORMANCE = "performance"
    SECURITY = "security"
    LEARNING = "learning"


class Notification:
    """A notification message."""

    def __init__(self, title: str, message: str, notification_type: NotificationType,
                 priority: NotificationPriority = NotificationPriority.MEDIUM,
                 agent_id: Optional[str] = None, metadata: Dict = None):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.priority = priority
        self.agent_id = agent_id
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.read = False
        self.dismissed = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type.value,
            "priority": self.priority.value,
            "agent_id": self.agent_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "read": self.read,
            "dismissed": self.dismissed,
        }


class MonitoringMetric:
    """A monitoring metric."""

    def __init__(self, name: str, value: float, unit: str = "",
                 threshold_high: Optional[float] = None,
                 threshold_low: Optional[float] = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        self.timestamp = datetime.utcnow()
        self.history: List[Dict] = []

    def update(self, value: float):
        """Update metric value."""
        self.history.append({
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
        })
        # Keep last 100 values
        if len(self.history) > 100:
            self.history = self.history[-100:]

        self.value = value
        self.timestamp = datetime.utcnow()

    def check_thresholds(self) -> Optional[str]:
        """Check if value exceeds thresholds."""
        if self.threshold_high and self.value > self.threshold_high:
            return f"HIGH: {self.name} = {self.value}{self.unit} (threshold: {self.threshold_high})"
        if self.threshold_low and self.value < self.threshold_low:
            return f"LOW: {self.name} = {self.value}{self.unit} (threshold: {self.threshold_low})"
        return None


class NotificationSystem:
    """Central notification and monitoring system."""

    def __init__(self):
        self.notifications: List[Notification] = []
        self.metrics: Dict[str, MonitoringMetric] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.alert_rules: List[Dict] = []
        self.max_notifications = 500
        self._monitoring_task = None

    async def notify(self, title: str, message: str, 
                    notification_type: NotificationType = NotificationType.SYSTEM,
                    priority: NotificationPriority = NotificationPriority.MEDIUM,
                    agent_id: Optional[str] = None, metadata: Dict = None) -> Notification:
        """Create and send a notification."""
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            agent_id=agent_id,
            metadata=metadata
        )

        self.notifications.append(notification)

        # Maintain size limit
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]

        # Notify subscribers
        await self._notify_subscribers(notification)

        return notification

    async def get_notifications(self, unread_only: bool = False,
                                notification_type: Optional[NotificationType] = None,
                                priority: Optional[NotificationPriority] = None,
                                limit: int = 50) -> List[Dict]:
        """Get notifications with filtering."""
        result = self.notifications

        if unread_only:
            result = [n for n in result if not n.read and not n.dismissed]

        if notification_type:
            result = [n for n in result if n.notification_type == notification_type]

        if priority:
            result = [n for n in result if n.priority == priority]

        # Sort by priority and time
        priority_order = {
            NotificationPriority.CRITICAL: 0,
            NotificationPriority.HIGH: 1,
            NotificationPriority.MEDIUM: 2,
            NotificationPriority.LOW: 3,
        }
        result.sort(key=lambda n: (priority_order[n.priority], n.created_at), reverse=True)

        return [n.to_dict() for n in result[:limit]]

    async def mark_as_read(self, notification_id: str):
        """Mark notification as read."""
        for n in self.notifications:
            if n.id == notification_id:
                n.read = True
                return True
        return False

    async def dismiss_notification(self, notification_id: str):
        """Dismiss a notification."""
        for n in self.notifications:
            if n.id == notification_id:
                n.dismissed = True
                return True
        return False

    async def clear_all(self):
        """Clear all notifications."""
        self.notifications = []

    # ========== Metrics ==========

    async def record_metric(self, name: str, value: float, unit: str = "",
                           threshold_high: Optional[float] = None,
                           threshold_low: Optional[float] = None):
        """Record a monitoring metric."""
        if name not in self.metrics:
            self.metrics[name] = MonitoringMetric(
                name=name, value=value, unit=unit,
                threshold_high=threshold_high,
                threshold_low=threshold_low
            )
        else:
            self.metrics[name].update(value)

        # Check thresholds
        alert = self.metrics[name].check_thresholds()
        if alert:
            await self.notify(
                title="Metric Alert",
                message=alert,
                notification_type=NotificationType.ALERT,
                priority=NotificationPriority.HIGH
            )

    async def get_metrics(self) -> Dict[str, Dict]:
        """Get all current metrics."""
        return {
            name: {
                "value": m.value,
                "unit": m.unit,
                "timestamp": m.timestamp.isoformat(),
                "history": m.history[-20:],  # Last 20 values
            }
            for name, m in self.metrics.items()
        }

    async def get_metric_history(self, name: str, hours: int = 24) -> List[Dict]:
        """Get metric history for a time period."""
        if name not in self.metrics:
            return []

        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            h for h in self.metrics[name].history
            if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]

    # ========== Subscribers ==========

    async def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to notifications."""
        self.subscribers[event_type].append(callback)

    async def _notify_subscribers(self, notification: Notification):
        """Notify all subscribers."""
        event_type = notification.notification_type.value
        for callback in self.subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(notification)
                else:
                    callback(notification)
            except Exception as e:
                print(f"Subscriber error: {e}")

    # ========== Alert Rules ==========

    async def add_alert_rule(self, metric_name: str, condition: str,
                            threshold: float, notification_type: NotificationType,
                            priority: NotificationPriority):
        """Add an alert rule."""
        self.alert_rules.append({
            "metric_name": metric_name,
            "condition": condition,  # above, below, equals
            "threshold": threshold,
            "notification_type": notification_type,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
        })

    async def check_alert_rules(self):
        """Check all alert rules against current metrics."""
        for rule in self.alert_rules:
            metric = self.metrics.get(rule["metric_name"])
            if not metric:
                continue

            triggered = False
            if rule["condition"] == "above" and metric.value > rule["threshold"]:
                triggered = True
            elif rule["condition"] == "below" and metric.value < rule["threshold"]:
                triggered = True

            if triggered:
                await self.notify(
                    title=f"Alert: {rule['metric_name']}",
                    message=f"{rule['metric_name']} is {rule['condition']} {rule['threshold']}",
                    notification_type=rule["notification_type"],
                    priority=rule["priority"]
                )

    # ========== System Monitoring ==========

    async def start_monitoring(self):
        """Start system monitoring loop."""
        import psutil

        while True:
            try:
                # CPU Usage
                cpu = psutil.cpu_percent(interval=1)
                await self.record_metric("cpu_usage", cpu, "%", threshold_high=80)

                # Memory Usage
                memory = psutil.virtual_memory()
                await self.record_metric("memory_usage", memory.percent, "%", threshold_high=85)

                # Disk Usage
                disk = psutil.disk_usage('/')
                await self.record_metric("disk_usage", disk.percent, "%", threshold_high=90)

                # Check alert rules
                await self.check_alert_rules()

                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(30)

    async def get_system_health(self) -> Dict:
        """Get overall system health."""
        import psutil

        return {
            "status": "healthy",  # or degraded, critical
            "cpu": {
                "usage": psutil.cpu_percent(interval=0.5),
                "cores": psutil.cpu_count(),
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
_notification_system: Optional[NotificationSystem] = None


async def get_notification_system() -> NotificationSystem:
    """Get or create the notification system singleton."""
    global _notification_system
    if _notification_system is None:
        _notification_system = NotificationSystem()
    return _notification_system
