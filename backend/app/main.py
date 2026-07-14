"""FastAPI main application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import get_settings
from app.models.agent import Agent
from app.models.skill import Skill
from app.models.memory import MemoryEntry, TrainingDataset, FeedbackEntry, KnowledgeGraphNode, KnowledgeGraphEdge
from app.models.task import Task
from app.routers import agents, skills, training, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()

    # Initialize MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            Agent,
            Skill,
            MemoryEntry,
            TrainingDataset,
            FeedbackEntry,
            KnowledgeGraphNode,
            KnowledgeGraphEdge,
            Task,
        ],
    )

    # Seed default skills if none exist
    await seed_default_skills()

    yield

    # Shutdown
    client.close()


async def seed_default_skills():
    """Seed default skills on startup."""
    from app.models.skill import Skill, SkillCategory, SkillTrigger, SkillExecutionMode

    default_skills = [
        {
            "name": "act-when-ready",
            "display_name": "Act When Ready",
            "description": "Prevent over-planning and execute decisively",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.MANUAL,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Execute tasks immediately when sufficient context exists. Do not over-plan.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "autonomous-continuation",
            "display_name": "Autonomous Continuation",
            "description": "Enable unattended runs without stalling",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Continue execution without asking for permission. Apply recovery automatically.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "effort-calibrator",
            "display_name": "Effort Calibrator",
            "description": "Pick appropriate effort level per workload",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Assess task complexity and apply appropriate effort level. Default to medium.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "no-gold-plating",
            "display_name": "No Gold Plating",
            "description": "Prevent unnecessary changes beyond the ask",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Change only what was requested. Do not refactor unrelated code or add unrequested features.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "grounded-progress",
            "display_name": "Grounded Progress",
            "description": "Report status with evidence, not assumptions",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Every status claim must have evidence. Never report based on assumption.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "scope-guard",
            "display_name": "Scope Guard",
            "description": "Maintain clear boundaries between diagnose, fix, review, implement",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Respect scope boundaries. Diagnose does not equal fix. Review does not equal implement.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "subagent-orchestration",
            "display_name": "Subagent Orchestration",
            "description": "Parallel delegation and verifier subagents",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.PARALLEL,
            "system_prompt": "Delegate independent subtasks to parallel agents. Use fresh-context verifiers.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "markdown-memory",
            "display_name": "Markdown Memory",
            "description": "File-based lesson memory with maintenance discipline",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Write lessons in markdown with concrete evidence. Review and archive monthly.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "skill-refactorer",
            "display_name": "Skill Refactorer",
            "description": "Meta-skill for auditing and improving other skills",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Audit skills for outdated patterns. Remove capability-compensation scaffolding. Keep real guardrails.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "regrounding-summary",
            "display_name": "Regrounding Summary",
            "description": "Final reports readable by newcomers",
            "category": SkillCategory.FABLE5,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Write final reports for someone who saw none of the work. No arrow chains or invented abbreviations.",
            "enabled": True,
            "is_core": True,
        },
        {
            "name": "auto-scaling",
            "display_name": "Auto-Scaling",
            "description": "Automatically create and destroy agents based on workload",
            "category": SkillCategory.SCALING,
            "trigger": SkillTrigger.CONDITIONAL,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Monitor workload and automatically scale agent pool. Scale up on high load, down on low load.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "load-balancer",
            "display_name": "Load Balancer",
            "description": "Distribute tasks across agents efficiently",
            "category": SkillCategory.ORCHESTRATION,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.PARALLEL,
            "system_prompt": "Distribute tasks using weighted round-robin, least connections, or capability-based strategies.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "error-recovery",
            "display_name": "Error Recovery",
            "description": "Automatic recovery from failures",
            "category": SkillCategory.ORCHESTRATION,
            "trigger": SkillTrigger.EVENT,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Detect errors and apply appropriate recovery strategies automatically. Max 3 retries.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "code-evolver",
            "display_name": "Code Evolver",
            "description": "Automatically analyze and improve code quality",
            "category": SkillCategory.LEARNING,
            "trigger": SkillTrigger.EVENT,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Analyze code for performance, security, and maintainability issues. Generate optimized versions.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "model-selector",
            "display_name": "Model Selector",
            "description": "Select optimal AI model per task",
            "category": SkillCategory.OPTIMIZATION,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Select cheapest adequate model based on complexity, budget, latency, and context requirements.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "context-optimizer",
            "display_name": "Context Optimizer",
            "description": "Maximize effective context window usage",
            "category": SkillCategory.OPTIMIZATION,
            "trigger": SkillTrigger.CONDITIONAL,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Compress, summarize, and prioritize context to fit within token limits while preserving critical information.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "multi-modal",
            "display_name": "Multi-Modal",
            "description": "Process images, audio, and text",
            "category": SkillCategory.MULTIMODAL,
            "trigger": SkillTrigger.MANUAL,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Process and understand images, audio, and text in unified workflows.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "collaboration",
            "display_name": "Collaboration",
            "description": "Enable multi-agent collaboration",
            "category": SkillCategory.COLLABORATION,
            "trigger": SkillTrigger.MANUAL,
            "execution_mode": SkillExecutionMode.PARALLEL,
            "system_prompt": "Coordinate multiple agents working together through structured communication protocols.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "security-guard",
            "display_name": "Security Guard",
            "description": "Protect sensitive data and prevent vulnerabilities",
            "category": SkillCategory.SECURITY,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.SYNC,
            "system_prompt": "Sanitize inputs, validate permissions, detect threats, and protect sensitive data.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "performance-monitor",
            "display_name": "Performance Monitor",
            "description": "Track and optimize system performance",
            "category": SkillCategory.MONITORING,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Collect metrics, detect anomalies, and alert on performance issues.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "data-pipeline",
            "display_name": "Data Pipeline",
            "description": "Process and transform data",
            "category": SkillCategory.LEARNING,
            "trigger": SkillTrigger.MANUAL,
            "execution_mode": SkillExecutionMode.BATCH,
            "system_prompt": "Ingest, clean, transform, validate, and export data efficiently.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "feedback-loop",
            "display_name": "Feedback Loop",
            "description": "Continuous learning through feedback",
            "category": SkillCategory.LEARNING,
            "trigger": SkillTrigger.EVENT,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Collect feedback, analyze patterns, and apply improvements to agent behavior.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "deployment-manager",
            "display_name": "Deployment Manager",
            "description": "Automate deployment with safety checks",
            "category": SkillCategory.DEPLOYMENT,
            "trigger": SkillTrigger.MANUAL,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Build, test, deploy, and monitor with automatic rollback on failure.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "cost-optimizer",
            "display_name": "Cost Optimizer",
            "description": "Minimize costs while maintaining quality",
            "category": SkillCategory.OPTIMIZATION,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Select cost-effective models, cache results, batch requests, and monitor spending.",
            "enabled": True,
            "is_core": False,
        },
        {
            "name": "knowledge-graph",
            "display_name": "Knowledge Graph",
            "description": "Build interconnected knowledge for reasoning",
            "category": SkillCategory.LEARNING,
            "trigger": SkillTrigger.AUTO,
            "execution_mode": SkillExecutionMode.ASYNC,
            "system_prompt": "Extract entities, identify relationships, and maintain a graph of interconnected knowledge.",
            "enabled": True,
            "is_core": False,
        },
    ]

    for skill_data in default_skills:
        existing = await Skill.find_one(Skill.name == skill_data["name"])
        if not existing:
            skill = Skill(**skill_data)
            await skill.insert()


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Startup - Multi-Agent System with 25 Skills",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router)
app.include_router(skills.router)
app.include_router(training.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "skills_count": 25,
        "features": [
            "Multi-Agent Orchestration",
            "Auto-Scaling",
            "Load Balancing",
            "Error Recovery",
            "Code Evolution",
            "Model Selection",
            "Context Optimization",
            "Multi-Modal Processing",
            "Agent Collaboration",
            "Security Guard",
            "Performance Monitoring",
            "Data Pipelines",
            "Feedback Loop",
            "Deployment Management",
            "Cost Optimization",
            "Knowledge Graph",
        ],
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    from app.models.agent import Agent
    from app.models.skill import Skill
    from app.models.task import Task

    return {
        "agents": await Agent.find().count(),
        "skills": await Skill.find().count(),
        "tasks": await Task.find().count(),
        "timestamp": datetime.utcnow().isoformat(),
    }
