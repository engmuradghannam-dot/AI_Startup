"""Skill management API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status

from app.models.skill import Skill, SkillCreate, SkillUpdate, SkillExecutionRequest, SkillCategory, SkillTrigger
from app.services.skill_engine import SkillEngine

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_skill(data: SkillCreate):
    """Create a new skill."""
    skill = Skill(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        category=data.category,
        trigger=data.trigger,
        execution_mode=data.execution_mode,
        parameters=data.parameters,
        prompt_template=data.prompt_template,
        system_prompt=data.system_prompt,
        config=data.config,
        depends_on=data.depends_on,
        tags=data.tags,
    )
    await skill.insert()
    return {"id": str(skill.id), "name": skill.name}


@router.get("/")
async def list_skills(
    category: Optional[SkillCategory] = None,
    enabled: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """List all skills."""
    query = {}
    if category:
        query["category"] = category
    if enabled is not None:
        query["enabled"] = enabled

    skills = await Skill.find(query).limit(limit).to_list()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "display_name": s.display_name,
            "category": s.category.value,
            "enabled": s.enabled,
            "trigger": s.trigger.value,
            "execution_mode": s.execution_mode.value,
            "metrics": {
                "total_executions": s.metrics.total_executions,
                "success_rate": s.metrics.successful_executions / max(s.metrics.total_executions, 1),
            },
        }
        for s in skills
    ]


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """Get skill by ID."""
    skill = await Skill.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {
        "id": str(skill.id),
        "name": skill.name,
        "display_name": skill.display_name,
        "description": skill.description,
        "category": skill.category.value,
        "trigger": skill.trigger.value,
        "execution_mode": skill.execution_mode.value,
        "parameters": [p.model_dump() for p in skill.parameters],
        "prompt_template": skill.prompt_template,
        "system_prompt": skill.system_prompt,
        "config": skill.config,
        "enabled": skill.enabled,
        "metrics": skill.metrics.model_dump(),
    }


@router.put("/{skill_id}")
async def update_skill(skill_id: str, data: SkillUpdate):
    """Update a skill."""
    skill = await Skill.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = data.model_dump(exclude_unset=True)
    await skill.update({"$set": update_data})

    return {"id": skill_id, "updated": True}


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str):
    """Delete a skill."""
    skill = await Skill.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await skill.delete()
    return None


@router.post("/{skill_id}/execute")
async def execute_skill(skill_id: str, request: SkillExecutionRequest):
    """Execute a skill."""
    engine = SkillEngine()
    result = await engine.execute_skill(request)
    return {
        "execution_id": result.execution_id,
        "status": result.status,
        "result": result.result,
        "tokens_used": result.tokens_used,
        "cost_usd": result.cost_usd,
        "execution_time_ms": result.execution_time_ms,
    }


@router.post("/batch-execute")
async def batch_execute_skills(requests: List[SkillExecutionRequest]):
    """Execute multiple skills in parallel."""
    engine = SkillEngine()
    results = await engine.batch_execute(requests)
    return [
        {
            "execution_id": r.execution_id,
            "status": r.status,
            "result": r.result,
        }
        for r in results
    ]


@router.get("/categories/summary")
async def get_categories_summary():
    """Get summary of skills by category."""
    from beanie.operators import In

    summary = {}
    for category in SkillCategory:
        count = await Skill.find(Skill.category == category).count()
        enabled = await Skill.find(Skill.category == category, Skill.enabled == True).count()
        summary[category.value] = {"total": count, "enabled": enabled}

    return summary
