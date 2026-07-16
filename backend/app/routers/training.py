"""Training and memory API routes - Enhanced with Agent Learning."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from datetime import datetime
import uuid
import json

from app.models.memory import TrainingDataset, MemoryEntry, FeedbackEntry, MemoryType
from app.services.self_learning import get_learning_system
from app.services.knowledge_graph import get_knowledge_graph_service

router = APIRouter(prefix="/training", tags=["Training"])

# In-memory storage for when DB is not available
_learning_sessions = {}
_agent_knowledge = {}


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
        dataset_id = str(uuid.uuid4())
        return {"id": dataset_id, "name": name, "status": "created_mock"}


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
        learning_system = await get_learning_system()
        await learning_system.record_interaction(
            agent_id=agent_id,
            query=task_id,
            response="",
            feedback={"rating": rating, "comment": comment, "skill_id": skill_id},
        )
        return {"id": str(uuid.uuid4()), "status": "submitted"}
    except Exception as e:
        return {"id": str(uuid.uuid4()), "status": "submitted_mock"}


@router.post("/feedback/process")
async def process_feedback(limit: int = Query(100, ge=1, le=1000)):
    """Process pending feedback."""
    try:
        learning_system = await get_learning_system()
        processed = 0
        for agent_id in list(learning_system.feedback_history.keys()):
            await learning_system.learn_from_feedback(agent_id)
            processed += len(learning_system.feedback_history[agent_id][:limit])
        return {"status": "processed", "processed": processed}
    except Exception as e:
        return {"status": "error", "message": str(e), "processed": 0}


@router.get("/feedback/stats")
async def get_feedback_stats(agent_id: Optional[str] = None):
    """Get feedback statistics."""
    try:
        learning_system = await get_learning_system()
        if not agent_id:
            return {
                "total_feedback": sum(len(h) for h in learning_system.feedback_history.values()),
                "average_rating": 0,
                "improvements": [],
                "agent_id": None,
            }
        return await learning_system.get_learning_stats(agent_id)
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


# ============================================
# NEW: Agent Learning System
# ============================================

@router.post("/learn")
async def train_agent(
    agent_id: str = Form(...),
    content: str = Form(...),
    content_type: str = Form("text"),  # text, image, video, document
    source: str = Form("manual"),  # manual, conversation, file, screen
    tags: str = Form(""),
):
    """Train an agent with new knowledge."""
    try:
        entry = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "content": content,
            "content_type": content_type,
            "source": source,
            "tags": tags.split(",") if tags else [],
            "timestamp": datetime.utcnow().isoformat(),
            "learned": True,
        }

        # Store in agent knowledge base
        if agent_id not in _agent_knowledge:
            _agent_knowledge[agent_id] = []
        _agent_knowledge[agent_id].append(entry)

        return {
            "status": "learned",
            "entry_id": entry["id"],
            "agent_id": agent_id,
            "knowledge_size": len(_agent_knowledge[agent_id]),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/learn/{agent_id}")
async def get_agent_knowledge(agent_id: str, query: Optional[str] = None):
    """Get all knowledge for an agent."""
    knowledge = _agent_knowledge.get(agent_id, [])

    if query:
        knowledge = [k for k in knowledge if query.lower() in k["content"].lower()]

    return {
        "agent_id": agent_id,
        "knowledge_count": len(knowledge),
        "knowledge": knowledge[-50:],  # Return last 50 entries
    }


@router.post("/learn/from-chat")
async def learn_from_chat(
    agent_id: str = Form(...),
    conversation: str = Form(...),
    user_feedback: Optional[int] = Form(None),
):
    """Learn from chat conversation."""
    try:
        entry = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "content": conversation,
            "content_type": "conversation",
            "source": "chat",
            "user_feedback": user_feedback,
            "timestamp": datetime.utcnow().isoformat(),
            "learned": True,
        }

        if agent_id not in _agent_knowledge:
            _agent_knowledge[agent_id] = []
        _agent_knowledge[agent_id].append(entry)

        return {
            "status": "learned_from_chat",
            "entry_id": entry["id"],
            "agent_id": agent_id,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/learn/screen")
async def learn_from_screen(
    agent_id: str = Form(...),
    description: str = Form(...),
    screen_data: Optional[str] = Form(None),
):
    """Learn from screen capture."""
    try:
        entry = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "content": description,
            "content_type": "screen",
            "source": "screen_capture",
            "screen_data": screen_data,
            "timestamp": datetime.utcnow().isoformat(),
            "learned": True,
        }

        if agent_id not in _agent_knowledge:
            _agent_knowledge[agent_id] = []
        _agent_knowledge[agent_id].append(entry)

        return {
            "status": "learned_from_screen",
            "entry_id": entry["id"],
            "agent_id": agent_id,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/learn/{agent_id}/{entry_id}")
async def delete_knowledge(agent_id: str, entry_id: str):
    """Delete a knowledge entry."""
    if agent_id in _agent_knowledge:
        _agent_knowledge[agent_id] = [
            k for k in _agent_knowledge[agent_id] if k["id"] != entry_id
        ]
        return {"status": "deleted", "agent_id": agent_id}
    return {"status": "not_found", "agent_id": agent_id}


# ============================================
# NEW: File Upload for Attachments
# ============================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    agent_id: str = Form(...),
    description: str = Form(""),
):
    """Upload a file (image, video, document) for agent learning."""
    try:
        content = await file.read()
        file_size = len(content)

        # Determine file type
        content_type = file.content_type or "application/octet-stream"
        if content_type.startswith("image/"):
            file_type = "image"
        elif content_type.startswith("video/"):
            file_type = "video"
        elif content_type.startswith("audio/"):
            file_type = "audio"
        else:
            file_type = "document"

        entry = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "filename": file.filename,
            "file_type": file_type,
            "content_type": content_type,
            "file_size": file_size,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "learned": True,
        }

        if agent_id not in _agent_knowledge:
            _agent_knowledge[agent_id] = []
        _agent_knowledge[agent_id].append(entry)

        return {
            "status": "uploaded",
            "entry_id": entry["id"],
            "agent_id": agent_id,
            "file_type": file_type,
            "file_size": file_size,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/uploads/{agent_id}")
async def get_agent_uploads(agent_id: str):
    """Get all uploaded files for an agent."""
    uploads = [
        k for k in _agent_knowledge.get(agent_id, [])
        if k.get("file_type") in ["image", "video", "audio", "document"]
    ]
    return {
        "agent_id": agent_id,
        "upload_count": len(uploads),
        "uploads": uploads,
    }
