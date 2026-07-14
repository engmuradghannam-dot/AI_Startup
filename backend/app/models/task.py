"""Task and execution models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from beanie import Document, Indexed
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution statuses."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(int, Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class Task(Document):
    """Task document model."""

    # Identity
    name: str
    description: str = ""
    task_type: str = "general"

    # Status
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL

    # Assignment
    assigned_agent_id: Optional[str] = None
    required_capabilities: List[str] = []
    required_skills: List[str] = []

    # Execution
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

    # Results
    result: Dict[str, Any] = {}
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None

    # Metrics
    tokens_used: int = 0
    cost_usd: float = 0.0
    execution_time_ms: float = 0.0
    retry_count: int = 0
    max_retries: int = 3

    # Dependencies
    depends_on: List[str] = []  # Task IDs
    required_by: List[str] = []

    # Subtasks
    parent_task_id: Optional[str] = None
    subtask_ids: List[str] = []

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None

    class Settings:
        name = "tasks"
        indexes = [
            "status",
            "priority",
            "assigned_agent_id",
            [("status", 1), ("priority", 1), ("created_at", 1)],
        ]


class TaskCreate(BaseModel):
    """Task creation request."""
    name: str
    description: str = ""
    task_type: str = "general"
    priority: TaskPriority = TaskPriority.NORMAL
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    required_capabilities: List[str] = []
    required_skills: List[str] = []
    depends_on: List[str] = []
    deadline: Optional[datetime] = None
    max_retries: int = 3


class TaskBatch(BaseModel):
    """Batch task execution request."""
    tasks: List[TaskCreate]
    parallel: bool = True
    max_concurrent: int = 10
    batch_name: str = ""
