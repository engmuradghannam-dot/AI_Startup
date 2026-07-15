"""Memory API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.advanced_memory import get_memory_system, MemoryEntry

router = APIRouter(prefix="/memory", tags=["Memory"])


# ========== Pydantic Models ==========

class MemoryCreateRequest(BaseModel):
    content: str
    agent_id: str
    memory_type: str = "episodic"
    importance: float = 0.5
    tags: List[str] = []
    metadata: dict = {}


class MemorySearchRequest(BaseModel):
    query: str
    agent_id: str
    memory_type: Optional[str] = None
    limit: int = 5


class MemoryResponse(BaseModel):
    id: str
    content: str
    agent_id: str
    memory_type: str
    importance: float
    tags: List[str]
    created_at: str
    access_count: int


class MemoryStatsResponse(BaseModel):
    agent_id: str
    total_memories: int
    episodic: int
    semantic: int
    procedural: int
    avg_importance: float
    total_accesses: int


# ========== Routes ==========

@router.post("/store", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def store_memory(request: MemoryCreateRequest):
    """Store a new memory."""
    memory_system = await get_memory_system()
    entry = await memory_system.store(
        content=request.content,
        agent_id=request.agent_id,
        memory_type=request.memory_type,
        importance=request.importance,
        tags=request.tags,
        metadata=request.metadata
    )
    return MemoryResponse(**entry.to_dict())


@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(request: MemorySearchRequest):
    """Search memories for an agent."""
    memory_system = await get_memory_system()
    results = await memory_system.retrieve(
        query=request.query,
        agent_id=request.agent_id,
        memory_type=request.memory_type,
        limit=request.limit
    )
    return [MemoryResponse(**r.to_dict()) for r in results]


@router.get("/agent/{agent_id}", response_model=List[MemoryResponse])
async def get_agent_memories(
    agent_id: str,
    memory_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    tag: Optional[str] = None,
):
    """Get all memories for an agent."""
    memory_system = await get_memory_system()

    if tag:
        results = await memory_system.retrieve_by_tags(agent_id, [tag], limit)
    else:
        results = await memory_system.retrieve(
            query="", agent_id=agent_id, memory_type=memory_type, limit=limit
        )

    return [MemoryResponse(**r.to_dict()) for r in results]


@router.get("/stats/{agent_id}", response_model=MemoryStatsResponse)
async def get_memory_stats(agent_id: str):
    """Get memory statistics for an agent."""
    memory_system = await get_memory_system()
    stats = await memory_system.get_memory_stats(agent_id)
    return MemoryStatsResponse(agent_id=agent_id, **stats)


@router.post("/consolidate/{agent_id}")
async def consolidate_memories(agent_id: str):
    """Consolidate memories for an agent."""
    memory_system = await get_memory_system()
    await memory_system.consolidate(agent_id)
    return {"message": f"Memories consolidated for agent {agent_id}"}


@router.post("/export/{agent_id}")
async def export_memories(agent_id: str):
    """Export all memories for an agent."""
    memory_system = await get_memory_system()
    memories = await memory_system.export_memories(agent_id)
    return {"agent_id": agent_id, "memories": memories, "count": len(memories)}


@router.post("/import/{agent_id}")
async def import_memories(agent_id: str, memories: List[dict]):
    """Import memories for an agent."""
    memory_system = await get_memory_system()
    await memory_system.import_memories(agent_id, memories)
    return {"message": f"Imported {len(memories)} memories for agent {agent_id}"}
