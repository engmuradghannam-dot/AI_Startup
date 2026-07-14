from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class Memory(BaseModel):
    id: Optional[str] = None
    agent_id: str
    content: str
    memory_type: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MemoryEntry(BaseModel):
    id: Optional[str] = None
    agent_id: str
    content: str
    memory_type: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

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
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    data: List = Field(default_factory=list)
    labels: List = Field(default_factory=list)
    model_type: str = "classification"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        protected_namespaces = ()

class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: List = Field(default_factory=list)
    labels: List = Field(default_factory=list)
    model_type: str = "classification"

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[List] = None
    labels: Optional[List] = None
    model_type: Optional[str] = None
