from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

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

class MemoryEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: Optional[str] = None
    agent_id: str
    content: str
    memory_type: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

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

class TrainingDataset(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    data: List = Field(default_factory=list)
    labels: List = Field(default_factory=list)
    dataset_type: str = "classification"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

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

class FeedbackEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: Optional[str] = None
    agent_id: str
    user_id: Optional[str] = None
    feedback_type: str = "general"
    content: str
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

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
