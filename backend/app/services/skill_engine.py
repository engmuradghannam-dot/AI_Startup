"""Skill execution engine."""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.skill import Skill, SkillExecutionRequest, SkillExecutionResponse, SkillTrigger, SkillExecutionMode
from app.models.agent import Agent
from app.services.groq_service import get_groq_service


class SkillEngine:
    """Engine for executing and managing skills."""

    def __init__(self):
        self._skill_cache: Dict[str, Skill] = {}
        self._execution_history: List[Dict] = []

    async def get_agent_skills(self, agent: Agent) -> List[Skill]:
        """Get all active skills for an agent."""
        skills = []
        for skill_id in agent.active_skills:
            skill = await Skill.get(skill_id)
            if skill and skill.enabled:
                skills.append(skill)
        return skills

    async def execute_skill(
        self,
        request: SkillExecutionRequest,
    ) -> SkillExecutionResponse:
        """Execute a skill."""
        skill = await Skill.get(request.skill_id)
        agent = await Agent.get(request.agent_id)

        if not skill or not agent:
            return SkillExecutionResponse(
                execution_id="",
                skill_id=request.skill_id,
                agent_id=request.agent_id,
                status="failed",
                result={"error": "Skill or agent not found"},
            )

        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()

        # Build skill prompt
        prompt = self._build_skill_prompt(skill, request)

        # Execute with Groq
        groq = await get_groq_service()

        messages = [
            {"role": "system", "content": skill.system_prompt},
            {"role": "user", "content": prompt},
        ]

        result = await groq.chat_completion(
            messages=messages,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Update skill metrics
        skill.metrics.total_executions += 1
        if result["success"]:
            skill.metrics.successful_executions += 1
        else:
            skill.metrics.failed_executions += 1
        skill.metrics.total_tokens_used += result["usage"].get("total_tokens", 0)
        skill.metrics.total_cost_usd += result["cost_usd"]
        skill.metrics.average_execution_time_ms = (
            (skill.metrics.average_execution_time_ms * (skill.metrics.total_executions - 1) + execution_time)
            / skill.metrics.total_executions
        )
        skill.metrics.last_executed = datetime.utcnow()
        await skill.save()

        return SkillExecutionResponse(
            execution_id=execution_id,
            skill_id=request.skill_id,
            agent_id=request.agent_id,
            status="completed" if result["success"] else "failed",
            result={"output": result["content"]} if result["success"] else {"error": result["error"]},
            tokens_used=result["usage"].get("total_tokens", 0),
            cost_usd=result["cost_usd"],
            execution_time_ms=execution_time,
            created_at=start_time,
            completed_at=datetime.utcnow(),
        )

    def _build_skill_prompt(self, skill: Skill, request: SkillExecutionRequest) -> str:
        """Build execution prompt for a skill."""
        prompt = skill.prompt_template

        # Replace parameters
        for param in skill.parameters:
            value = request.parameters.get(param.name, param.default)
            if value is not None:
                prompt = prompt.replace(f"{{{param.name}}}", str(value))

        # Add context
        if request.context:
            prompt += f"\n\nContext: {request.context}"

        return prompt

    async def batch_execute(
        self,
        requests: List[SkillExecutionRequest],
        max_concurrent: int = 10,
    ) -> List[SkillExecutionResponse]:
        """Execute multiple skills in parallel."""
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _exec(req):
            async with semaphore:
                return await self.execute_skill(req)

        tasks = [_exec(req) for req in requests]
        return await asyncio.gather(*tasks)

    async def auto_trigger_skills(
        self,
        agent: Agent,
        context: Dict[str, Any],
    ) -> List[SkillExecutionResponse]:
        """Auto-trigger skills based on context."""
        triggered = []

        skills = await Skill.find(
            Skill.trigger == SkillTrigger.AUTO,
            Skill.enabled == True,
        ).to_list()

        for skill in skills:
            if self._should_trigger(skill, context):
                request = SkillExecutionRequest(
                    skill_id=str(skill.id),
                    agent_id=str(agent.id),
                    parameters=context.get("parameters", {}),
                    context=context,
                )
                result = await self.execute_skill(request)
                triggered.append(result)

        return triggered

    def _should_trigger(self, skill: Skill, context: Dict[str, Any]) -> bool:
        """Determine if a skill should be triggered."""
        # Simple keyword matching - can be enhanced with ML
        task_type = context.get("task_type", "")
        for cap in skill.provides_capabilities:
            if cap.lower() in task_type.lower():
                return True
        return False
