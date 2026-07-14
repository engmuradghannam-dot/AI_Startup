"""Training and memory API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from app.models.memory import TrainingDataset, MemoryEntry, FeedbackEntry, MemoryType
from app.services.feedback_loop import get_feedback_loop
from app.services.knowledge_graph import get_knowledge_graph_service

router = APIRouter(prefix="/training", tags=["Training"])


@router.post("/datasets")
async def create_dataset(name: str, description: str = "", dataset_type: str = "conversations"):
    """Create a training dataset."""
    dataset = TrainingDataset(
        name=name,
        description=description,
        dataset_type=dataset_type,
    )
    await dataset.insert()
    return {"id": str(dataset.id), "name": name}


@router.get("/datasets")
async def list_datasets(limit: int = Query(100, ge=1, le=1000)):
    """List training datasets."""
    datasets = await TrainingDataset.find().limit(limit).to_list()
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "type": d.dataset_type,
            "entries": d.entry_count,
            "quality": d.quality_score,
        }
        for d in datasets
    ]


@router.post("/datasets/{dataset_id}/entries")
async def add_dataset_entry(dataset_id: str, entry: dict):
    """Add entry to dataset."""
    dataset = await TrainingDataset.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset.entries.append(entry)
    dataset.entry_count = len(dataset.entries)
    await dataset.save()

    return {"dataset_id": dataset_id, "entry_count": dataset.entry_count}


@router.post("/feedback")
async def submit_feedback(
    agent_id: str,
    task_id: str,
    rating: int,
    comment: str = "",
    skill_id: Optional[str] = None,
):
    """Submit feedback for learning."""
    feedback_loop = await get_feedback_loop()
    feedback = await feedback_loop.submit_feedback(
        agent_id=agent_id,
        task_id=task_id,
        rating=rating,
        comment=comment,
        skill_id=skill_id,
    )
    return {"id": str(feedback.id), "status": "submitted"}


@router.post("/feedback/process")
async def process_feedback(limit: int = Query(100, ge=1, le=1000)):
    """Process pending feedback."""
    feedback_loop = await get_feedback_loop()
    result = await feedback_loop.batch_process_feedback(limit)
    return result


@router.get("/feedback/stats")
async def get_feedback_stats(agent_id: Optional[str] = None):
    """Get feedback statistics."""
    feedback_loop = await get_feedback_loop()
    return await feedback_loop.get_learning_stats(agent_id)


@router.get("/memory/{agent_id}")
async def get_agent_memory(agent_id: str, memory_type: Optional[MemoryType] = None):
    """Get agent memory entries."""
    query = {"agent_id": agent_id}
    if memory_type:
        query["memory_type"] = memory_type

    memories = await MemoryEntry.find(query).sort(-MemoryEntry.created_at).limit(100).to_list()
    return [
        {
            "id": str(m.id),
            "type": m.memory_type.value,
            "importance": m.importance.value,
            "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
            "tags": m.tags,
            "created_at": m.created_at.isoformat(),
        }
        for m in memories
    ]


@router.get("/knowledge-graph/{agent_id}")
async def get_agent_knowledge_graph(agent_id: str):
    """Get knowledge graph for an agent."""
    kg = await get_knowledge_graph_service()
    return await kg.get_agent_knowledge(agent_id)


@router.post("/knowledge-graph/nodes")
async def add_knowledge_node(
    node_id: str,
    node_type: str,
    label: str,
    description: str = "",
    properties: Optional[dict] = None,
):
    """Add node to knowledge graph."""
    kg = await get_knowledge_graph_service()
    node = await kg.add_node(node_id, node_type, label, description, properties or {})
    return {"id": node_id, "type": node_type, "label": label}


@router.post("/knowledge-graph/edges")
async def add_knowledge_edge(
    source_id: str,
    target_id: str,
    relation_type: str,
    weight: float = 1.0,
):
    """Add edge to knowledge graph."""
    kg = await get_knowledge_graph_service()
    edge = await kg.add_edge(source_id, target_id, relation_type, weight=weight)
    return {"edge_id": edge.edge_id, "relation": relation_type}


@router.get("/knowledge-graph/stats")
async def get_knowledge_graph_stats():
    """Get knowledge graph statistics."""
    kg = await get_knowledge_graph_service()
    return kg.get_graph_stats()
