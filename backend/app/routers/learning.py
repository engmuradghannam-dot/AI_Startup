"""Learning API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.self_learning import get_learning_system

router = APIRouter(prefix="/learning", tags=["Learning"])


# ========== Pydantic Models ==========

class FeedbackRequest(BaseModel):
    agent_id: str
    query: str
    response: str
    rating: int  # 1-5
    correction: Optional[str] = None
    comments: Optional[str] = None


class LearningStatsResponse(BaseModel):
    agent_id: str
    total_patterns_learned: int
    pattern_types: dict
    total_interactions: int
    successful_interactions: int
    user_satisfaction: float
    improvement_rate: float
    feedback_count: int
    avg_confidence: float


class KnowledgeExportResponse(BaseModel):
    agent_id: str
    patterns: List[dict]
    metrics: dict
    feedback_count: int


# ========== Routes ==========

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for an interaction."""
    learning_system = await get_learning_system()

    feedback = {
        "rating": request.rating,
        "correction": request.correction,
        "comments": request.comments,
    }

    await learning_system.record_interaction(
        agent_id=request.agent_id,
        query=request.query,
        response=request.response,
        feedback=feedback
    )

    # try to extract patterns right away so feedback has a visible effect quickly,
    # rather than only on the next manual "trigger learning" call
    await learning_system.learn_from_feedback(request.agent_id)

    return {
        "message": "Feedback recorded successfully",
        "agent_id": request.agent_id,
        "rating": request.rating,
    }


@router.get("/stats/{agent_id}", response_model=LearningStatsResponse)
async def get_learning_stats(agent_id: str):
    """Get learning statistics for an agent."""
    learning_system = await get_learning_system()
    stats = await learning_system.get_learning_stats(agent_id)
    return LearningStatsResponse(agent_id=agent_id, **stats)


@router.post("/learn/{agent_id}")
async def trigger_learning(agent_id: str):
    """Manually trigger learning for an agent."""
    learning_system = await get_learning_system()
    await learning_system.learn_from_feedback(agent_id)
    return {"message": f"Learning triggered for agent {agent_id}"}


@router.get("/export/{agent_id}", response_model=KnowledgeExportResponse)
async def export_knowledge(agent_id: str):
    """Export learned knowledge for an agent."""
    learning_system = await get_learning_system()
    knowledge = await learning_system.export_knowledge(agent_id)
    return KnowledgeExportResponse(agent_id=agent_id, **knowledge)


@router.post("/import/{agent_id}")
async def import_knowledge(agent_id: str, knowledge: dict):
    """Import learned knowledge for an agent."""
    learning_system = await get_learning_system()
    await learning_system.import_knowledge(agent_id, knowledge)
    return {"message": f"Knowledge imported for agent {agent_id}"}


@router.get("/patterns/{agent_id}")
async def get_patterns(agent_id: str, pattern_type: Optional[str] = None):
    """Get learned patterns for an agent."""
    learning_system = await get_learning_system()
    patterns = learning_system.patterns.get(agent_id, [])

    if pattern_type:
        patterns = [p for p in patterns if p.pattern_type == pattern_type]

    return {
        "agent_id": agent_id,
        "patterns": [p.to_dict() for p in patterns],
        "count": len(patterns),
    }
