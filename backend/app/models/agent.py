"""Agent data models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from beanie import Document, Indexed
from enum import Enum


class AgentStatus(str, Enum):
    """Agent lifecycle statuses."""
    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    LEARNING = "learning"
    SCALING = "scaling"
    TERMINATED = "terminated"


class AgentRole(str, Enum):
    """Predefined agent roles."""
    GENERAL = "general"
    MARKETING = "marketing"
    LEGAL = "legal"
    FINANCE = "finance"
    HR = "hr"
    HEALTHCARE = "healthcare"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    ANALYST = "analyst"
    MANAGER = "manager"
    RESEARCHER = "researcher"
    SECURITY = "security"
    DEVOPS = "devops"
    DATA_SCIENTIST = "data_scientist"


class AgentCapability(BaseModel):
    """Agent capability definition."""
    name: str
    description: str
    skill_ids: List[str] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    usage_count: int = 0


class AgentMetrics(BaseModel):
    """Agent performance metrics."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_active: Optional[datetime] = None
    learning_iterations: int = 0
    self_improvements: int = 0


class AgentMemory(BaseModel):
    """Agent memory and context."""
    short_term: List[Dict[str, Any]] = []  # Recent interactions
    long_term: List[Dict[str, Any]] = []   # Important lessons
    context_window: List[str] = []         # Current context
    knowledge_graph_nodes: List[str] = []  # Connected knowledge


class Agent(Document):
    """Agent document model."""

    # Identity
    name: str = Indexed(str)
    role: AgentRole = AgentRole.GENERAL
    description: str = ""
    version: str = "1.0.0"

    # Status
    status: AgentStatus = AgentStatus.IDLE
    priority: int = Field(default=5, ge=1, le=10)

    # Capabilities
    capabilities: List[AgentCapability] = []
    active_skills: List[str] = []

    # Memory
    memory: AgentMemory = Field(default_factory=AgentMemory)

    # Metrics
    metrics: AgentMetrics = Field(default_factory=AgentMetrics)

    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    max_tokens: int = 4096
    temperature: float = 0.7
    model: str = "llama-3.3-70b-versatile"

    # Relationships
    parent_agent_id: Optional[str] = None
    child_agent_ids: List[str] = []
    collaborator_ids: List[str] = []

    # Scaling
    is_auto_scaled: bool = False
    scale_group: str = "default"

    # Security
    permissions: List[str] = ["read", "execute"]
    allowed_domains: List[str] = []

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_task_at: Optional[datetime] = None

    class Settings:
        name = "agents"
        indexes = [
            "status",
            "role",
            "scale_group",
            [("name", 1), ("status", 1)],
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Marketing Agent Alpha",
                "role": "marketing",
                "description": "AI agent specialized in marketing strategies",
                "status": "idle",
                "priority": 7,
            }
        }


class AgentCreate(BaseModel):
    """Agent creation request."""
    name: str
    role: AgentRole = AgentRole.GENERAL
    description: str = ""
    capabilities: List[AgentCapability] = []
    config: Dict[str, Any] = {}
    priority: int = 5
    parent_agent_id: Optional[str] = None


class AgentUpdate(BaseModel):
    """Agent update request."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    priority: Optional[int] = None
    capabilities: Optional[List[AgentCapability]] = None
    config: Optional[Dict[str, Any]] = None
    active_skills: Optional[List[str]] = None


class AgentResponse(BaseModel):
    """Agent response model."""
    id: str
    name: str
    role: str
    status: str
    description: str
    metrics: AgentMetrics
    created_at: datetime
    updated_at: datetime
