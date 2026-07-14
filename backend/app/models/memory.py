from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class Memory(BaseModel):
    id: Optional[str] = None
    agent_id: str
    content: str
    memory_type: str = "general"  # general, skill, conversation, task
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
