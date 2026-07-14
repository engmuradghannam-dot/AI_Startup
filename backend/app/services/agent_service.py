"""Agent management and orchestration service."""
import asyncio
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.agent import Agent, AgentCreate, AgentUpdate, AgentStatus, AgentRole, AgentCapability
from app.models.task import Task, TaskCreate, TaskStatus
from app.services.groq_service import get_groq_service
from app.services.skill_engine import SkillEngine


class AgentService:
    """Service for managing AI agents."""

    def __init__(self):
        self.skill_engine = SkillEngine()
        self._active_agents: Dict[str, Agent] = {}
        self._agent_tasks: Dict[str, List[str]] = {}

    async def create_agent(self, data: AgentCreate) -> Agent:
        """Create a new agent."""
        agent = Agent(
            id=str(uuid.uuid4()),
            name=data.name,
            role=data.role,
            description=data.description,
            capabilities=data.capabilities,
            config=data.config,
            priority=data.priority,
            parent_agent_id=data.parent_agent_id,
            status=AgentStatus.IDLE,
        )
        await agent.insert()
        self._active_agents[agent.id] = agent
        return agent

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return await Agent.get(agent_id)

    async def list_agents(
        self,
        status: Optional[AgentStatus] = None,
        role: Optional[AgentRole] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Agent]:
        """List agents with optional filtering."""
        query = {}
        if status:
            query["status"] = status
        if role:
            query["role"] = role

        return await Agent.find(query).skip(skip).limit(limit).to_list()

    async def update_agent(self, agent_id: str, data: AgentUpdate) -> Optional[Agent]:
        """Update agent."""
        agent = await Agent.get(agent_id)
        if not agent:
            return None

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await agent.update({"$set": update_data})
        return await Agent.get(agent_id)

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent."""
        agent = await Agent.get(agent_id)
        if not agent:
            return False
        await agent.delete()
        self._active_agents.pop(agent_id, None)
        return True

    async def execute_task(self, agent_id: str, task: Task) -> Dict[str, Any]:
        """Execute a task with an agent."""
        agent = await Agent.get(agent_id)
        if not agent:
            return {"success": False, "error": "Agent not found"}

        # Update agent status
        agent.status = AgentStatus.BUSY
        agent.metrics.last_active = datetime.utcnow()
        await agent.save()

        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        task.assigned_agent_id = agent_id
        await task.save()

        try:
            # Get relevant skills
            active_skills = await self.skill_engine.get_agent_skills(agent)

            # Build system prompt
            system_prompt = self._build_system_prompt(agent, active_skills)

            # Execute with Groq
            groq = await get_groq_service()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._build_task_prompt(task)},
            ]

            result = await groq.chat_completion(
                messages=messages,
                model=agent.model,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
            )

            # Update task
            if result["success"]:
                task.status = TaskStatus.COMPLETED
                task.result = {"output": result["content"]}
                task.tokens_used = result["usage"].get("total_tokens", 0)
                task.cost_usd = result["cost_usd"]
                task.execution_time_ms = result["execution_time_ms"]

                # Update agent metrics
                agent.metrics.tasks_completed += 1
                agent.metrics.total_tokens_used += task.tokens_used
                agent.metrics.total_cost_usd += task.cost_usd
            else:
                task.status = TaskStatus.FAILED
                task.error_message = result["error"]
                agent.metrics.tasks_failed += 1

            task.completed_at = datetime.utcnow()
            await task.save()

            # Update agent status
            agent.status = AgentStatus.IDLE
            await agent.save()

            return {
                "success": result["success"],
                "task_id": str(task.id),
                "agent_id": agent_id,
                "result": task.result if result["success"] else {"error": task.error_message},
                "metrics": {
                    "tokens_used": task.tokens_used,
                    "cost_usd": task.cost_usd,
                    "execution_time_ms": task.execution_time_ms,
                }
            }

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await task.save()

            agent.status = AgentStatus.ERROR
            agent.metrics.tasks_failed += 1
            await agent.save()

            return {"success": False, "error": str(e)}

    def _build_system_prompt(self, agent: Agent, skills: List[Any]) -> str:
        """Build system prompt for agent."""
        prompt = f"""You are {agent.name}, an AI agent specialized in {agent.role.value}.
{agent.description}

Your capabilities:
"""
        for cap in agent.capabilities:
            prompt += f"- {cap.name}: {cap.description}\n"

        prompt += f"\nActive skills: {', '.join(agent.active_skills)}\n"
        prompt += "\nExecute tasks efficiently and report results clearly."

        return prompt

    def _build_task_prompt(self, task: Task) -> str:
        """Build task prompt."""
        return f"""Task: {task.name}
Description: {task.description}
Type: {task.task_type}

Parameters:
{task.parameters}

Context:
{task.context}

Please execute this task and provide the results."""

    async def clone_agent(self, agent_id: str, new_name: str) -> Optional[Agent]:
        """Clone an existing agent."""
        original = await Agent.get(agent_id)
        if not original:
            return None

        cloned = Agent(
            id=str(uuid.uuid4()),
            name=new_name,
            role=original.role,
            description=original.description,
            capabilities=original.capabilities,
            config=original.config,
            priority=original.priority,
            parent_agent_id=agent_id,
            active_skills=original.active_skills,
            model=original.model,
            temperature=original.temperature,
            max_tokens=original.max_tokens,
        )
        await cloned.insert()

        # Update parent
        original.child_agent_ids.append(cloned.id)
        await original.save()

        return cloned

    async def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive agent metrics."""
        agent = await Agent.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}

        # Get task history
        tasks = await Task.find(Task.assigned_agent_id == agent_id).to_list()

        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]

        return {
            "agent_id": agent_id,
            "name": agent.name,
            "status": agent.status.value,
            "metrics": {
                "tasks_completed": len(completed),
                "tasks_failed": len(failed),
                "success_rate": len(completed) / (len(completed) + len(failed)) * 100 if (len(completed) + len(failed)) > 0 else 0,
                "total_tokens_used": agent.metrics.total_tokens_used,
                "total_cost_usd": agent.metrics.total_cost_usd,
                "average_response_time_ms": agent.metrics.average_response_time_ms,
                "learning_iterations": agent.metrics.learning_iterations,
                "self_improvements": agent.metrics.self_improvements,
            },
            "capabilities": [c.name for c in agent.capabilities],
            "active_skills": agent.active_skills,
            "created_at": agent.created_at.isoformat(),
            "last_active": agent.metrics.last_active.isoformat() if agent.metrics.last_active else None,
        }


# Singleton
_agent_service: Optional[AgentService] = None


async def get_agent_service() -> AgentService:
    """Get or create agent service."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
