"""Memory and training data models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from beanie import Document, Indexed
from enum import Enum


class MemoryType(str, Enum):
    """Types of memory entries."""
    INTERACTION = "interaction"
    LESSON = "lesson"
    ERROR = "error"
    SUCCESS = "success"
    CODE = "code"
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    FEEDBACK = "feedback"


class MemoryImportance(str, Enum):
    """Memory importance levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class MemoryEntry(Document):
    """Memory entry document."""

    agent_id: str = Indexed(str)
    memory_type: MemoryType = MemoryType.INTERACTION
    importance: MemoryImportance = MemoryImportance.MEDIUM

    # Content
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = []

    # Context
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    skill_id: Optional[str] = None

    # Relationships
    related_memory_ids: List[str] = []
    knowledge_graph_edges: List[Dict[str, str]] = []

    # Metrics
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    class Settings:
        name = "memories"
        indexes = [
            "agent_id",
            "memory_type",
            "importance",
            [("agent_id", 1), ("memory_type", 1), ("created_at", -1)],
        ]


class TrainingDataset(Document):
    """Training dataset document."""

    name: str = Indexed(str)
    description: str = ""
    dataset_type: str = "conversations"  # conversations, code, qa, instructions

    # Content
    entries: List[Dict[str, Any]] = []
    entry_count: int = 0

    # Metadata
    source: str = "system"
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    tags: List[str] = []

    # Usage
    used_by_agents: List[str] = []
    used_by_skills: List[str] = []
    usage_count: int = 0

    # Status
    is_processed: bool = False
    is_approved: bool = True

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "training_datasets"


class FeedbackEntry(Document):
    """Feedback entry for learning."""

    agent_id: str
    skill_id: Optional[str] = None
    task_id: str

    # Feedback
    rating: int = Field(default=3, ge=1, le=5)
    comment: str = ""
    expected_output: Optional[str] = None
    actual_output: str = ""

    # Context
    context: Dict[str, Any] = {}

    # Processing
    processed: bool = False
    improvement_applied: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "feedback_entries"


class KnowledgeGraphNode(Document):
    """Knowledge graph node."""

    node_id: str = Indexed(str)
    node_type: str  # concept, entity, skill, agent, task
    label: str
    description: str = ""
    properties: Dict[str, Any] = {}

    # Relationships
    incoming_edges: List[str] = []
    outgoing_edges: List[str] = []

    # Metadata
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "system"

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "knowledge_graph_nodes"


class KnowledgeGraphEdge(Document):
    """Knowledge graph edge/relationship."""

    edge_id: str = Indexed(str)
    source_node_id: str
    target_node_id: str
    relation_type: str

    properties: Dict[str, Any] = {}
    weight: float = Field(default=1.0, ge=0.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "knowledge_graph_edges"
