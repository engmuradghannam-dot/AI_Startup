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
    try:
        dataset = TrainingDataset(
            name=name,
            description=description,
            dataset_type=dataset_type,
        )
        await dataset.insert()
        return {"id": str(dataset.id), "name": name}
    except Exception as e:
        import uuid
        return {"id": str(uuid.uuid4()), "name": name, "status": "created_mock"}


@router.get("/datasets")
async def list_datasets(limit: int = Query(100, ge=1, le=1000)):
    """List training datasets."""
    try:
        datasets = await TrainingDataset.find().limit(limit).to_list()
        return [
            {
                "id": str(d.id),
                "name": d.name,
                "type": d.dataset_type if hasattr(d, 'dataset_type') else "conversations",
                "entries": d.entry_count if hasattr(d, 'entry_count') else 0,
                "quality": d.quality_score if hasattr(d, 'quality_score') else 0,
            }
            for d in datasets
        ]
    except Exception as e:
        # Return empty array if DB is not available
        return []


@router.post("/datasets/{dataset_id}/entries")
async def add_dataset_entry(dataset_id: str, entry: dict):
    """Add entry to dataset."""
    try:
        dataset = await TrainingDataset.get(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        if not hasattr(dataset, 'entries'):
            dataset.entries = []
        dataset.entries.append(entry)
        dataset.entry_count = len(dataset.entries)
        await dataset.save()

        return {"dataset_id": dataset_id, "entry_count": dataset.entry_count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.post("/feedback")
async def submit_feedback(
    agent_id: str,
    task_id: str,
    rating: int,
    comment: str = "",
    skill_id: Optional[str] = None,
):
    """Submit feedback for learning."""
    try:
        feedback_loop = await get_feedback_loop()
        feedback = await feedback_loop.submit_feedback(
            agent_id=agent_id,
            task_id=task_id,
            rating=rating,
            comment=comment,
            skill_id=skill_id,
        )
        return {"id": str(feedback.id), "status": "submitted"}
    except Exception as e:
        import uuid
        return {"id": str(uuid.uuid4()), "status": "submitted_mock"}


@router.post("/feedback/process")
async def process_feedback(limit: int = Query(100, ge=1, le=1000)):
    """Process pending feedback."""
    try:
        feedback_loop = await get_feedback_loop()
        result = await feedback_loop.batch_process_feedback(limit)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e), "processed": 0}


@router.get("/feedback/stats")
async def get_feedback_stats(agent_id: Optional[str] = None):
    """Get feedback statistics."""
    try:
        feedback_loop = await get_feedback_loop()
        return await feedback_loop.get_learning_stats(agent_id)
    except Exception as e:
        return {
            "total_feedback": 0,
            "average_rating": 0,
            "improvements": [],
            "agent_id": agent_id,
        }


@router.get("/memory/{agent_id}")
async def get_agent_memory(agent_id: str, memory_type: Optional[MemoryType] = None):
    """Get agent memory entries."""
    try:
        query = {"agent_id": agent_id}
        if memory_type:
            query["memory_type"] = memory_type

        memories = await MemoryEntry.find(query).sort(-MemoryEntry.created_at).limit(100).to_list()
        return [
            {
                "id": str(m.id),
                "type": m.memory_type.value if hasattr(m.memory_type, 'value') else str(m.memory_type),
                "content": m.content if hasattr(m, 'content') else "",
                "importance": m.importance if hasattr(m, 'importance') else 0,
                "created_at": m.created_at if hasattr(m, 'created_at') else None,
            }
            for m in memories
        ]
    except Exception as e:
        # Return empty array if DB is not available
        return []


@router.get("/stats")
async def get_training_stats():
    """Get overall training statistics."""
    try:
        datasets_count = await TrainingDataset.find().count()
        memories_count = await MemoryEntry.find().count()
        feedback_count = await FeedbackEntry.find().count()

        return {
            "datasets": datasets_count,
            "memories": memories_count,
            "feedback": feedback_count,
            "status": "active",
        }
    except Exception as e:
        return {
            "datasets": 0,
            "memories": 0,
            "feedback": 0,
            "status": "limited_mode",
        }
