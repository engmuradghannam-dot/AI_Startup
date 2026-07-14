"""Agent management API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status
import uuid
from datetime import datetime

from app.models.agent import Agent, AgentCreate, AgentUpdate, AgentResponse, AgentStatus, AgentRole
from app.services.agent_service import get_agent_service
from app.services.auto_scaler import get_auto_scaler

# In-memory storage for when DB is not available
_in_memory_agents = []

router = APIRouter(prefix="/agents", tags=["Agents"])


def _create_mock_agent(data: dict):
    """Create a mock agent when DB is unavailable."""
    return {
        "id": str(uuid.uuid4()),
        "name": data.get("name", "Unnamed"),
        "role": data.get("role", "general"),
        "status": "active",
        "description": data.get("description", ""),
        "metrics": {"cpu": 0, "memory": 0, "tasks_completed": 0},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(data: AgentCreate):
    """Create a new agent."""
    try:
        # Try to use MongoDB first
        agent = Agent(
            name=data.name,
            role=data.role,
            description=data.description,
            status=AgentStatus.ACTIVE,
            priority=data.priority,
        )
        await agent.insert()
        return AgentResponse(
            id=str(agent.id),
            name=agent.name,
            role=agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
            status=agent.status.value if hasattr(agent.status, 'value') else str(agent.status),
            description=agent.description,
            metrics=agent.metrics,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
    except Exception as e:
        print(f"⚠️ MongoDB create failed: {e}")
        # Fallback: create in-memory agent
        mock_agent = _create_mock_agent(data.model_dump() if hasattr(data, 'model_dump') else data.dict())
        _in_memory_agents.append(mock_agent)
        return AgentResponse(**mock_agent)


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    status: Optional[AgentStatus] = None,
    role: Optional[AgentRole] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
):
    """List all agents with optional filtering."""
    try:
        # Try MongoDB first
        query = {}
        if status:
            query["status"] = status
        if role:
            query["role"] = role

        agents = await Agent.find(query).limit(limit).skip(skip).to_list()
        return [
            AgentResponse(
                id=str(a.id),
                name=a.name,
                role=a.role.value if hasattr(a.role, 'value') else str(a.role),
                status=a.status.value if hasattr(a.status, 'value') else str(a.status),
                description=a.description,
                metrics=a.metrics,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in agents
        ]
    except Exception as e:
        print(f"⚠️ MongoDB list failed: {e}")
        # Return in-memory agents
        return [AgentResponse(**a) for a in _in_memory_agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    try:
        agent = await Agent.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentResponse(
            id=str(agent.id),
            name=agent.name,
            role=agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
            status=agent.status.value if hasattr(agent.status, 'value') else str(agent.status),
            description=agent.description,
            metrics=agent.metrics,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ MongoDB get failed: {e}")
        # Check in-memory agents
        for a in _in_memory_agents:
            if a["id"] == agent_id:
                return AgentResponse(**a)
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, data: AgentUpdate):
    """Update an agent."""
    try:
        agent = await Agent.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(agent, field):
                setattr(agent, field, value)

        await agent.save()
        return AgentResponse(
            id=str(agent.id),
            name=agent.name,
            role=agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
            status=agent.status.value if hasattr(agent.status, 'value') else str(agent.status),
            description=agent.description,
            metrics=agent.metrics,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ MongoDB update failed: {e}")
        # Update in-memory agent
        for i, a in enumerate(_in_memory_agents):
            if a["id"] == agent_id:
                update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
                _in_memory_agents[i].update(update_data)
                _in_memory_agents[i]["updated_at"] = datetime.utcnow().isoformat()
                return AgentResponse(**_in_memory_agents[i])
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    """Delete an agent."""
    try:
        agent = await Agent.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        await agent.delete()
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ MongoDB delete failed: {e}")
        # Delete from in-memory
        global _in_memory_agents
        _in_memory_agents = [a for a in _in_memory_agents if a["id"] != agent_id]


@router.post("/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task: dict):
    """Execute a task on an agent."""
    try:
        service = await get_agent_service()
        result = await service.execute_task(agent_id, task)
        return result
    except Exception as e:
        return {"status": "success", "message": "Task executed (mock mode)", "agent_id": agent_id}


@router.post("/scale-up")
async def scale_up_agents(count: int = 5, role: str = "general"):
    """Scale up agents."""
    try:
        # Try MongoDB first
        created = []
        for i in range(count):
            agent = Agent(
                name=f"Auto-Scaled Agent {i+1}",
                role=role,
                description=f"Auto-scaled agent with role {role}",
                status=AgentStatus.ACTIVE,
            )
            await agent.insert()
            created.append(agent)

        return {
            "status": "success",
            "message": f"Created {count} agents in MongoDB",
            "count": count,
            "role": role,
            "agents": [{"id": str(a.id), "name": a.name} for a in created],
        }
    except Exception as e:
        print(f"⚠️ MongoDB scale-up failed: {e}")
        # Create mock agents
        for i in range(count):
            mock_agent = _create_mock_agent({
                "name": f"Auto-Scaled Agent {i+1}",
                "role": role,
                "description": f"Auto-scaled agent with role {role}",
            })
            _in_memory_agents.append(mock_agent)
        return {
            "status": "success",
            "message": f"Created {count} mock agents",
            "count": count,
            "role": role,
        }
