"""Skill data models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from beanie import Document, Indexed
from enum import Enum


class SkillCategory(str, Enum):
    """Skill categories."""
    FABLE5 = "fable5"
    ORCHESTRATION = "orchestration"
    SCALING = "scaling"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    MONITORING = "monitoring"
    LEARNING = "learning"
    DEPLOYMENT = "deployment"
    MULTIMODAL = "multimodal"
    COLLABORATION = "collaboration"


class SkillTrigger(str, Enum):
    """Skill trigger types."""
    AUTO = "auto"
    MANUAL = "manual"
    EVENT = "event"
    SCHEDULE = "schedule"
    CONDITIONAL = "conditional"


class SkillExecutionMode(str, Enum):
    """Skill execution modes."""
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"
    BATCH = "batch"


class SkillParameter(BaseModel):
    """Skill parameter definition."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    validation_rules: Dict[str, Any] = {}


class SkillMetrics(BaseModel):
    """Skill execution metrics."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time_ms: float = 0.0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    last_executed: Optional[datetime] = None


class Skill(Document):
    """Skill document model."""

    # Identity
    name: str = Indexed(str)
    display_name: str = ""
    description: str = ""
    category: SkillCategory = SkillCategory.FABLE5
    version: str = "1.0.0"

    # Execution
    trigger: SkillTrigger = SkillTrigger.AUTO
    execution_mode: SkillExecutionMode = SkillExecutionMode.ASYNC

    # Configuration
    parameters: List[SkillParameter] = []
    config: Dict[str, Any] = Field(default_factory=dict)

    # Content
    prompt_template: str = ""
    system_prompt: str = ""
    verification_hooks: List[str] = []
    error_handlers: List[str] = []

    # Capabilities
    required_capabilities: List[str] = []
    provides_capabilities: List[str] = []

    # Dependencies
    depends_on: List[str] = []  # Skill IDs this skill depends on
    required_by: List[str] = []  # Skill IDs that depend on this

    # Metrics
    metrics: SkillMetrics = Field(default_factory=SkillMetrics)

    # Training
    training_data_refs: List[str] = []
    fine_tuned: bool = False

    # Status
    enabled: bool = True
    is_core: bool = False  # Core skills cannot be disabled

    # Metadata
    author: str = "system"
    tags: List[str] = []

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "skills"
        indexes = [
            "category",
            "enabled",
            "trigger",
            [("name", 1), ("category", 1)],
        ]


class SkillCreate(BaseModel):
    """Skill creation request."""
    name: str
    display_name: str
    description: str
    category: SkillCategory
    trigger: SkillTrigger = SkillTrigger.AUTO
    execution_mode: SkillExecutionMode = SkillExecutionMode.ASYNC
    parameters: List[SkillParameter] = []
    prompt_template: str = ""
    system_prompt: str = ""
    config: Dict[str, Any] = {}
    depends_on: List[str] = []
    tags: List[str] = []


class SkillUpdate(BaseModel):
    """Skill update request."""
    display_name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    prompt_template: Optional[str] = None
    system_prompt: Optional[str] = None
    parameters: Optional[List[SkillParameter]] = None


class SkillExecutionRequest(BaseModel):
    """Skill execution request."""
    skill_id: str
    agent_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 5
    timeout_seconds: int = 300


class SkillExecutionResponse(BaseModel):
    """Skill execution response."""
    execution_id: str
    skill_id: str
    agent_id: str
    status: str
    result: Dict[str, Any] = {}
    tokens_used: int = 0
    cost_usd: float = 0.0
    execution_time_ms: float = 0.0
    created_at: datetime
    completed_at: Optional[datetime] = None
