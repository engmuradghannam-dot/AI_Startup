from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from beanie import Document, Indexed

class MemoryType(str, Enum):
    GENERAL = "general"
    CONVERSATION = "conversation"
    SKILL = "skill"
    TASK = "task"
    KNOWLEDGE = "knowledge"
    FEEDBACK = "feedback"

class FeedbackType(str, Enum):
    GENERAL = "general"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    SUGGESTION = "suggestion"
    BUG = "bug"

class DatasetType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NLP = "nlp"
    IMAGE = "image"

class Memory(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: Optional[str] = None
    agent_id: str
    content: str
    memory_type: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class MemoryEntry(Document):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    agent_id: Indexed(str)
    content: str
    memory_type: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "memory_entries"


class LearningPatternDoc(Document):
    """Persisted learned pattern, so self-learning survives a server restart."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    agent_id: Indexed(str)
    pattern_type: str  # preference, correction, enhancement
    trigger: str
    response: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source: str = "interaction"
    usage_count: int = 0
    success_rate: float = 0.5
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "learning_patterns"

class MemoryCreate(BaseModel):
    agent_id: str
    content: str
    memory_type: str = "general"
    importance: float = 0.5
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    memory_type: Optional[str] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class TrainingDataset(Document):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    name: str
    description: Optional[str] = None
    data: List = Field(default_factory=list)
    labels: List = Field(default_factory=list)
    dataset_type: str = "classification"
    entries: List = Field(default_factory=list)
    entry_count: int = 0
    quality_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "training_datasets"

class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: List = Field(default_factory=list)
    labels: List = Field(default_factory=list)
    dataset_type: str = "classification"

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[List] = None
    labels: Optional[List] = None
    dataset_type: Optional[str] = None

class FeedbackEntry(Document):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    agent_id: Indexed(str)
    user_id: Optional[str] = None
    feedback_type: str = "general"
    content: str
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "feedback_entries"

class FeedbackCreate(BaseModel):
    agent_id: str
    user_id: Optional[str] = None
    feedback_type: str = "general"
    content: str
    rating: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FeedbackUpdate(BaseModel):
    feedback_type: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
