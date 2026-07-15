"""Multi-Agent Orchestrator with Fable 5 Skills.

4 Specialized Agents using Groq Cloud API:
- strategist: Planning & Decision Making
- coder: Software Development
- analyst: Data Analysis & Research
- coordinator: Task Coordination & Synthesis

10 Fable 5 Skills integrated.
"""
import json
import logging
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import asyncio

from app.services.unified_ai_service import get_unified_ai_service

logger = logging.getLogger(__name__)


class Agent:
    """Individual AI agent with specialty, skills, and memory."""

    def __init__(
        self,
        name: str,
        specialty: str,
        system_prompt: str,
        skills: List[str],
        model: str,
        description: str = "",
    ):
        self.name = name
        self.specialty = specialty
        self.system_prompt = system_prompt
        self.skills = skills
        self.model = model
        self.description = description
        self.memory: List[Dict[str, Any]] = []
        self.metrics = {
            "tasks_completed": 0,
            "total_tokens": 0,
            "average_response_time_ms": 0.0,
        }

    async def think(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute agent thinking process."""
        start_time = datetime.utcnow()

        memory_context = ""
        if self.memory:
            recent_memories = self.memory[-5:]
            memory_context = "\n".join([
                f"- [{m.get('role', 'unknown')}]: {str(m.get('content', ''))[:200]}"
                for m in recent_memories
            ])

        prompt = f"""You are {self.name}, an AI agent specialized in {self.specialty}.

Your capabilities: {', '.join(self.skills)}

Previous context:
{memory_context}

Current Task: {task}

Additional Context: {json.dumps(context or {})}

Think step by step and provide your best response."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        ai = await get_unified_ai_service()
        result = await ai.chat_completion(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=2048,
        )

        content = result.get("content", "")

        self.memory.append({"role": "user", "content": task, "timestamp": start_time.isoformat()})
        self.memory.append({"role": "assistant", "content": content, "timestamp": datetime.utcnow().isoformat()})

        self.metrics["tasks_completed"] += 1
        usage = result.get("usage", {})
        self.metrics["total_tokens"] += usage.get("total_tokens", 0)

        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        n = self.metrics["tasks_completed"]
        self.metrics["average_response_time_ms"] = (
            (self.metrics["average_response_time_ms"] * (n - 1) + elapsed) / n
        )

        return {
            "agent": self.name,
            "specialty": self.specialty,
            "thought": content,
            "model_used": result.get("model", self.model),
            "provider": result.get("provider", "unknown"),
            "source": result.get("source", "unknown"),
            "metrics": {
                "response_time_ms": elapsed,
                "tokens_used": usage.get("total_tokens", 0),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


class MultiAgentOrchestrator:
    """Orchestrate multiple agents for complex tasks."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._create_default_agents()
        self._execution_history: List[Dict[str, Any]] = []

    def _create_default_agents(self):
        """Create the 4 core specialized agents using Groq models."""

        agent_configs = [
            {
                "name": "strategist",
                "specialty": "Strategic Planning & Decision Making",
                "description": "Analyzes situations, identifies goals, and creates actionable plans",
                "system_prompt": """You are a strategic planning AI agent. Your role is to:
1. Analyze complex situations and identify key objectives
2. Evaluate different approaches and their trade-offs
3. Create structured, actionable plans
4. Assess risks and contingencies
5. Use the act-when-ready skill to determine optimal timing
6. Apply effort-calibrator to match effort to complexity

Always think step by step and provide clear, structured output.""",
                "skills": ["act-when-ready", "effort-calibrator", "scope-guard", "grounded-progress"],
                "model": "llama-3.1-70b-versatile",
            },
            {
                "name": "coder",
                "specialty": "Software Development & Code Generation",
                "description": "Writes clean, efficient, well-documented code",
                "system_prompt": """You are an expert software developer AI agent. Your role is to:
1. Write clean, efficient, well-documented code
2. Follow best practices and design patterns
3. Consider edge cases and error handling
4. Use no-gold-plating skill to avoid over-engineering
5. Apply skill-refactorer to improve existing code
6. Use autonomous-continuation for iterative development

Always provide production-ready code with comments and explanations.""",
                "skills": ["no-gold-plating", "skill-refactorer", "autonomous-continuation", "scope-guard"],
                "model": "llama-3.1-70b-versatile",
            },
            {
                "name": "analyst",
                "specialty": "Data Analysis & Research",
                "description": "Extracts insights, identifies patterns, provides evidence-based conclusions",
                "system_prompt": """You are a data analysis and research AI agent. Your role is to:
1. Extract meaningful insights from data and text
2. Identify patterns, trends, and anomalies
3. Provide evidence-based conclusions
4. Use grounded-progress to track real progress
5. Apply regrounding-summary for fresh perspectives
6. Use markdown-memory for structured knowledge storage

Always cite evidence and provide structured, analytical output.""",
                "skills": ["grounded-progress", "regrounding-summary", "markdown-memory", "effort-calibrator"],
                "model": "llama-3.1-70b-versatile",
            },
            {
                "name": "coordinator",
                "specialty": "Task Coordination & Synthesis",
                "description": "Synthesizes outputs, resolves conflicts, produces unified responses",
                "system_prompt": """You are a master coordination AI agent. Your role is to:
1. Synthesize outputs from multiple agents into coherent responses
2. Resolve conflicts and contradictions between different perspectives
3. Ensure consistency and completeness
4. Use subagent-orchestration to coordinate team efforts
5. Apply markdown-memory for context preservation
6. Use scope-guard to stay within boundaries

Always produce unified, well-structured final outputs.""",
                "skills": ["subagent-orchestration", "markdown-memory", "scope-guard", "regrounding-summary"],
                "model": "llama-3.1-70b-versatile",
            },
        ]

        for config in agent_configs:
            self.agents[config["name"]] = Agent(**config)

    def get_agent(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": agent.name,
                "specialty": agent.specialty,
                "description": agent.description,
                "skills": agent.skills,
                "model": agent.model,
                "metrics": agent.metrics,
            }
            for agent in self.agents.values()
        ]

    async def execute_single(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a single agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        result = await agent.think(task, context)

        self._execution_history.append({
            "type": "single",
            "agent": agent_name,
            "task": task,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return result

    async def execute_multi(
        self,
        task: str,
        mode: Literal["sequential", "parallel", "hierarchical", "swarm"] = "hierarchical",
        agent_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute multiple agents in specified mode."""

        agent_names = agent_names or list(self.agents.keys())
        selected_agents = {k: v for k, v in self.agents.items() if k in agent_names}

        if not selected_agents:
            raise ValueError("No valid agents selected")

        trace = []
        start_time = datetime.utcnow()

        if mode == "sequential":
            current_context = dict(context or {})
            for name, agent in selected_agents.items():
                enriched_task = f"{task}\n\nPrevious analysis: {current_context.get('previous_output', 'None')}"
                result = await agent.think(enriched_task, current_context)
                trace.append(result)
                current_context["previous_output"] = result["thought"]
                current_context["previous_agent"] = name

        elif mode == "parallel":
            tasks = [
                agent.think(task, context)
                for agent in selected_agents.values()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            trace = [r for r in results if not isinstance(r, Exception)]

        elif mode == "hierarchical":
            strategy_result = await self.agents["strategist"].think(
                f"Create a detailed plan for: {task}",
                context
            )
            trace.append(strategy_result)
            plan = strategy_result["thought"]

            execution_agents = [n for n in agent_names if n != "strategist" and n != "coordinator"]
            execution_tasks = []
            for name in execution_agents:
                agent = self.agents[name]
                execution_task = f"""Execute your part of this plan:

Plan: {plan}

Original Task: {task}

Your specialty: {agent.specialty}
Focus on your area of expertise."""
                execution_tasks.append(agent.think(execution_task, context))

            if execution_tasks:
                execution_results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                trace.extend([r for r in execution_results if not isinstance(r, Exception)])

            synthesis_input = f"""Synthesize these outputs into a unified response:

Task: {task}
Plan: {plan}

Agent Outputs:
"""
            for t in trace:
                synthesis_input += f"\n--- {t['agent']} ---\n{t['thought'][:500]}\n"

            coordinator_result = await self.agents["coordinator"].think(synthesis_input, context)
            trace.append(coordinator_result)

        elif mode == "swarm":
            shared_memory = []
            num_rounds = context.get("swarm_rounds", 2) if context else 2

            for round_num in range(num_rounds):
                round_tasks = []
                for name, agent in selected_agents.items():
                    swarm_context = {
                        **(context or {}),
                        "shared_memory": shared_memory,
                        "round": round_num + 1,
                        "total_rounds": num_rounds,
                    }
                    swarm_task = f"""Collaborative round {round_num + 1}/{num_rounds}.

Task: {task}

Shared insights from previous rounds:
{"\n".join(shared_memory[-5:])}

Build upon previous insights and contribute new perspectives."""
                    round_tasks.append(agent.think(swarm_task, swarm_context))

                round_results = await asyncio.gather(*round_tasks, return_exceptions=True)
                valid_results = [r for r in round_results if not isinstance(r, Exception)]

                for r in valid_results:
                    shared_memory.append(f"{r['agent']}: {r['thought'][:300]}")

                trace.extend(valid_results)

            final_task = f"""Create final unified response based on all collaborative rounds:

Task: {task}

All contributions:
{"\n".join(shared_memory)}"""

            final_result = await self.agents["coordinator"].think(final_task, context)
            trace.append(final_result)

        else:
            raise ValueError(f"Unknown mode: {mode}")

        elapsed = (datetime.utcnow() - start_time).total_seconds()

        self._execution_history.append({
            "type": "multi",
            "mode": mode,
            "agents": list(selected_agents.keys()),
            "task": task,
            "duration_seconds": elapsed,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "mode": mode,
            "task": task,
            "agents_used": list(selected_agents.keys()),
            "agent_trace": trace,
            "final_output": trace[-1]["thought"] if trace else "No output generated",
            "duration_seconds": elapsed,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def execute_with_skills(
        self,
        task: str,
        skills: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute task with specific skills applied."""
        best_agent = None
        max_skill_match = 0

        for name, agent in self.agents.items():
            match = len(set(agent.skills) & set(skills))
            if match > max_skill_match:
                max_skill_match = match
                best_agent = agent

        if not best_agent:
            best_agent = self.agents["coordinator"]

        skill_context = {
            **(context or {}),
            "required_skills": skills,
            "skill_match": max_skill_match,
        }

        result = await best_agent.think(task, skill_context)
        result["skills_applied"] = skills
        result["matched_agent"] = best_agent.name

        return result

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._execution_history[-limit:]

    def clear_memory(self, agent_name: Optional[str] = None):
        if agent_name:
            agent = self.get_agent(agent_name)
            if agent:
                agent.memory.clear()
        else:
            for agent in self.agents.values():
                agent.memory.clear()


_orchestrator = None


async def get_multi_agent_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
    return _orchestrator
