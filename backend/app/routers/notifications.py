"""Notifications API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.notification_system import (
    get_notification_system, NotificationType, NotificationPriority
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ========== Pydantic Models ==========

class CreateNotificationRequest(BaseModel):
    title: str
    message: str
    notification_type: str = "system"
    priority: str = "medium"
    agent_id: Optional[str] = None
    metadata: dict = {}


class AlertRuleRequest(BaseModel):
    metric_name: str
    condition: str  # above, below, equals
    threshold: float
    notification_type: str = "alert"
    priority: str = "high"


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    priority: str
    agent_id: Optional[str]
    created_at: str
    read: bool


# ========== Routes ==========

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
):
    """Get notifications with filtering."""
    notification_system = await get_notification_system()

    type_enum = NotificationType(notification_type) if notification_type else None
    priority_enum = NotificationPriority(priority) if priority else None

    notifications = await notification_system.get_notifications(
        unread_only=unread_only,
        notification_type=type_enum,
        priority=priority_enum,
        limit=limit
    )
    return [NotificationResponse(**n) for n in notifications]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notification(request: CreateNotificationRequest):
    """Create a new notification."""
    notification_system = await get_notification_system()

    notification = await notification_system.notify(
        title=request.title,
        message=request.message,
        notification_type=NotificationType(request.notification_type),
        priority=NotificationPriority(request.priority),
        agent_id=request.agent_id,
        metadata=request.metadata
    )

    return notification.to_dict()


@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Mark notification as read."""
    notification_system = await get_notification_system()
    success = await notification_system.mark_as_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.post("/{notification_id}/dismiss")
async def dismiss_notification(notification_id: str):
    """Dismiss a notification."""
    notification_system = await get_notification_system()
    success = await notification_system.dismiss_notification(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification dismissed"}


@router.delete("/")
async def clear_all_notifications():
    """Clear all notifications."""
    notification_system = await get_notification_system()
    await notification_system.clear_all()
    return {"message": "All notifications cleared"}


# ========== Metrics ==========

@router.get("/metrics")
async def get_metrics():
    """Get all monitoring metrics."""
    notification_system = await get_notification_system()
    metrics = await notification_system.get_metrics()
    return metrics


@router.get("/metrics/{metric_name}")
async def get_metric_history(metric_name: str, hours: int = 24):
    """Get metric history."""
    notification_system = await get_notification_system()
    history = await notification_system.get_metric_history(metric_name, hours)
    return {"metric": metric_name, "history": history}


@router.post("/metrics/record")
async def record_metric(name: str, value: float, unit: str = "",
                       threshold_high: Optional[float] = None,
                       threshold_low: Optional[float] = None):
    """Record a metric."""
    notification_system = await get_notification_system()
    await notification_system.record_metric(name, value, unit, threshold_high, threshold_low)
    return {"message": f"Metric {name} recorded"}


# ========== Alert Rules ==========

@router.post("/alert-rules", status_code=status.HTTP_201_CREATED)
async def add_alert_rule(request: AlertRuleRequest):
    """Add an alert rule."""
    notification_system = await get_notification_system()
    await notification_system.add_alert_rule(
        metric_name=request.metric_name,
        condition=request.condition,
        threshold=request.threshold,
        notification_type=NotificationType(request.notification_type),
        priority=NotificationPriority(request.priority)
    )
    return {"message": "Alert rule added"}


# ========== System Health ==========

@router.get("/system/health")
async def get_system_health():
    """Get system health status."""
    notification_system = await get_notification_system()
    health = await notification_system.get_system_health()
    return health


@router.get("/unread-count")
async def get_unread_count():
    """Get count of unread notifications."""
    notification_system = await get_notification_system()
    notifications = await notification_system.get_notifications(unread_only=True, limit=1000)
    return {"unread_count": len(notifications)}
