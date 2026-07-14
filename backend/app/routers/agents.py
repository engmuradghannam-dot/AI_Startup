"""Agent management API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status

from app.models.agent import Agent, AgentCreate, AgentUpdate, AgentResponse, AgentStatus, AgentRole
from app.services.agent_service import get_agent_service
from app.services.auto_scaler import get_auto_scaler
from app.services.load_balancer import get_load_balancer

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(data: AgentCreate):
    """Create a new agent."""
    service = await get_agent_service()
    agent = await service.create_agent(data)
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        role=agent.role.value,
        status=agent.status.value,
        description=agent.description,
        metrics=agent.metrics,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    status: Optional[AgentStatus] = None,
    role: Optional[AgentRole] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
):
    """List all agents with optional filtering."""
    service = await get_agent_service()
    agents = await service.list_agents(status=status, role=role, limit=limit, skip=skip)
    return [
        AgentResponse(
            id=str(a.id),
            name=a.name,
            role=a.role.value,
            status=a.status.value,
            description=a.description,
            metrics=a.metrics,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in agents
    ]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    service = await get_agent_service()
    agent = await service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        role=agent.role.value,
        status=agent.status.value,
        description=agent.description,
        metrics=agent.metrics,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, data: AgentUpdate):
    """Update an agent."""
    service = await get_agent_service()
    agent = await service.update_agent(agent_id, data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        role=agent.role.value,
        status=agent.status.value,
        description=agent.description,
        metrics=agent.metrics,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    """Delete an agent."""
    service = await get_agent_service()
    success = await service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return None


@router.post("/{agent_id}/clone")
async def clone_agent(agent_id: str, new_name: str):
    """Clone an existing agent."""
    service = await get_agent_service()
    cloned = await service.clone_agent(agent_id, new_name)
    if not cloned:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"id": str(cloned.id), "name": cloned.name, "parent_id": agent_id}


@router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    """Get agent performance metrics."""
    service = await get_agent_service()
    metrics = await service.get_agent_metrics(agent_id)
    if "error" in metrics:
        raise HTTPException(status_code=404, detail=metrics["error"])
    return metrics


@router.post("/{agent_id}/execute")
async def execute_task(agent_id: str, task_data: dict):
    """Execute a task with an agent."""
    from app.models.task import Task, TaskCreate, TaskStatus

    service = await get_agent_service()
    agent = await service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Create task
    task = Task(
        name=task_data.get("name", "Unnamed task"),
        description=task_data.get("description", ""),
        task_type=task_data.get("task_type", "general"),
        parameters=task_data.get("parameters", {}),
        context=task_data.get("context", {}),
    )
    await task.insert()

    # Execute
    result = await service.execute_task(agent_id, task)
    return result


@router.get("/scaling/metrics")
async def get_scaling_metrics():
    """Get auto-scaling metrics."""
    scaler = await get_auto_scaler()
    return await scaler.get_current_metrics()


@router.post("/scaling/scale-up")
async def manual_scale_up(count: int = Query(1, ge=1, le=100), role: str = "general"):
    """Manually scale up agents."""
    scaler = await get_auto_scaler()
    from app.models.agent import AgentRole
    role_enum = AgentRole(role) if role in [r.value for r in AgentRole] else AgentRole.GENERAL
    agents = await scaler._scale_up(count, role_enum)
    return {"created": len(agents), "agent_ids": [str(a.id) for a in agents]}


@router.get("/load/metrics")
async def get_load_metrics():
    """Get load balancer metrics."""
    lb = await get_load_balancer()
    return await lb.get_load_metrics()
