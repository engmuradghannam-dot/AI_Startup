"""
AI Startup - Multi-Agent System with Groq API
Backend: FastAPI + Groq + Multi-Agent Orchestration
"""

import os
import json
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq
import redis.asyncio as redis

# ── Configuration ─────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Groq Models
GROQ_MODELS = {
    "llama-4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b": "llama-3.3-70b-versatile",
    "llama-3.1-8b": "llama-3.1-8b-instant",
    "gpt-oss-20b": "openai/gpt-oss-20b",
    "gpt-oss-120b": "openai/gpt-oss-120b",
    "qwen3-32b": "qwen/qwen3-32b",
    "kimi-k2": "moonshotai/kimi-k2-instruct-0905",
    "compound-beta": "compound-beta"
}

DEFAULT_MODEL = "llama-3.3-70b-versatile"

# ── Pydantic Models ───────────────────────────────────────────────────────────

class AgentConfig(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    max_tokens: int = 2048

class TaskConfig(BaseModel):
    description: str
    expected_output: str
    agent_name: str

class CrewRequest(BaseModel):
    name: str = "AI Startup Crew"
    agents: List[AgentConfig]
    tasks: List[TaskConfig]
    process: str = "sequential"  # sequential, parallel, hierarchical
    model: str = DEFAULT_MODEL

class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False

class AgentStatus(BaseModel):
    agent_id: str
    name: str
    status: str  # idle, running, completed, error
    current_task: Optional[str] = None
    last_output: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CrewStatus(BaseModel):
    crew_id: str
    name: str
    status: str  # pending, running, completed, error
    agents: List[AgentStatus]
    outputs: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

# ── Global State ──────────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Crew execution storage
active_crews: Dict[str, CrewStatus] = {}

# ── Groq Client ───────────────────────────────────────────────────────────────

groq_client = Groq(api_key=GROQ_API_KEY)

# ── Redis Client ──────────────────────────────────────────────────────────────

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        except:
            redis_client = None
    return redis_client

# ── Agent System ─────────────────────────────────────────────────────────────

class AIAgent:
    def __init__(self, config: AgentConfig, crew_id: str):
        self.config = config
        self.crew_id = crew_id
        self.agent_id = str(uuid.uuid4())
        self.status = "idle"
        self.current_task = None
        self.memory: List[Dict] = []
        self.client = groq_client

    async def execute_task(self, task: TaskConfig, context: str = "") -> str:
        self.status = "running"
        self.current_task = task.description

        # Build system prompt
        system_prompt = f"""You are {self.config.name}, an AI agent with the following role:

Role: {self.config.role}
Goal: {self.config.goal}
Backstory: {self.config.backstory}

You are part of a multi-agent crew. Execute the given task professionally and thoroughly.
"""

        # Build user prompt with context
        user_prompt = f"""Task: {task.description}

Expected Output: {task.expected_output}

Context from previous agents:
{context if context else "No previous context available."}

Please execute this task and provide your output."""

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            output = response.choices[0].message.content
            self.status = "completed"
            self.current_task = None

            # Store in memory
            self.memory.append({
                "task": task.description,
                "output": output,
                "timestamp": datetime.utcnow().isoformat()
            })

            return output

        except Exception as e:
            self.status = "error"
            self.current_task = None
            return f"Error executing task: {str(e)}"

    def get_status(self) -> AgentStatus:
        return AgentStatus(
            agent_id=self.agent_id,
            name=self.config.name,
            status=self.status,
            current_task=self.current_task,
            last_output=self.memory[-1]["output"] if self.memory else None
        )

class Crew:
    def __init__(self, request: CrewRequest):
        self.crew_id = str(uuid.uuid4())
        self.request = request
        self.agents: Dict[str, AIAgent] = {}
        self.status = "pending"
        self.outputs: List[Dict] = []
        self.created_at = datetime.utcnow()
        self.completed_at = None

        # Initialize agents
        for agent_config in request.agents:
            self.agents[agent_config.name] = AIAgent(agent_config, self.crew_id)

    async def run(self):
        self.status = "running"
        context = ""

        for i, task in enumerate(self.request.tasks):
            agent = self.agents.get(task.agent_name)
            if not agent:
                continue

            # Broadcast status update
            await manager.broadcast({
                "type": "agent_status",
                "crew_id": self.crew_id,
                "agent": agent.get_status().dict(),
                "task_index": i,
                "total_tasks": len(self.request.tasks)
            })

            # Execute task
            output = await agent.execute_task(task, context)

            # Store output
            task_output = {
                "task": task.description,
                "agent": task.agent_name,
                "output": output,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.outputs.append(task_output)

            # Update context for next agent
            context += f"\n\n--- Output from {task.agent_name} ---\n{output}"

            # Broadcast completion
            await manager.broadcast({
                "type": "task_complete",
                "crew_id": self.crew_id,
                "task_output": task_output,
                "progress": f"{i+1}/{len(self.request.tasks)}"
            })

        self.status = "completed"
        self.completed_at = datetime.utcnow()

        # Broadcast crew completion
        await manager.broadcast({
            "type": "crew_complete",
            "crew_id": self.crew_id,
            "outputs": self.outputs
        })

    def get_status(self) -> CrewStatus:
        return CrewStatus(
            crew_id=self.crew_id,
            name=self.request.name,
            status=self.status,
            agents=[agent.get_status() for agent in self.agents.values()],
            outputs=self.outputs,
            created_at=self.created_at,
            completed_at=self.completed_at
        )

# ── FastAPI App ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    r = await get_redis()
    if r:
        await r.set("ai_startup_status", "online")
    yield
    # Shutdown
    if redis_client:
        await redis_client.close()

app = FastAPI(
    title="AI Startup - Multi-Agent System",
    description="AI Army of 100,000 Agents with Groq API Integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "AI Startup API",
        "version": "1.0.0",
        "status": "online",
        "groq_models": list(GROQ_MODELS.keys()),
        "features": [
            "Multi-Agent Orchestration",
            "Groq API Integration",
            "Real-time WebSocket Updates",
            "Self-Improving Code",
            "Collaborative Learning"
        ]
    }

@app.get("/models")
async def get_models():
    return {
        "models": GROQ_MODELS,
        "default": DEFAULT_MODEL,
        "recommended_for_agents": ["llama-3.3-70b", "llama-3.1-8b", "compound-beta"]
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        response = groq_client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )

        if request.stream:
            # For streaming, we'd need to return a StreamingResponse
            # Simplified here for the example
            content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
            return {"content": content, "model": request.model, "streaming": True}

        return {
            "content": response.choices[0].message.content,
            "model": request.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crew/create")
async def create_crew(request: CrewRequest, background_tasks: BackgroundTasks):
    crew = Crew(request)
    active_crews[crew.crew_id] = crew

    # Run crew in background
    background_tasks.add_task(crew.run)

    return {
        "crew_id": crew.crew_id,
        "status": "created",
        "message": "Crew is starting execution..."
    }

@app.get("/crew/{crew_id}/status")
async def get_crew_status(crew_id: str):
    crew = active_crews.get(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return crew.get_status()

@app.get("/crew/{crew_id}/results")
async def get_crew_results(crew_id: str):
    crew = active_crews.get(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return {
        "crew_id": crew_id,
        "status": crew.status,
        "outputs": crew.outputs,
        "completed_at": crew.completed_at
    }

@app.get("/crews")
async def list_crews():
    return {
        "crews": [
            {
                "crew_id": crew.crew_id,
                "name": crew.request.name,
                "status": crew.status,
                "agents_count": len(crew.agents),
                "tasks_count": len(crew.request.tasks),
                "created_at": crew.created_at
            }
            for crew in active_crews.values()
        ]
    }

@app.post("/agent/self-improve")
async def self_improve(agent_config: AgentConfig):
    """
    Self-improving code feature - agent analyzes its own performance
    and suggests improvements to its configuration.
    """
    try:
        improvement_prompt = f"""You are an AI optimization expert. Analyze the following agent configuration and suggest specific improvements to make it more effective:

Current Agent Configuration:
- Name: {agent_config.name}
- Role: {agent_config.role}
- Goal: {agent_config.goal}
- Backstory: {agent_config.backstory}
- Model: {agent_config.model}
- Temperature: {agent_config.temperature}

Please provide:
1. Strengths of current configuration
2. Areas for improvement
3. Suggested changes to role/goal/backstory
4. Recommended model and parameters
5. Actionable optimization tips

Return your analysis in structured JSON format."""

        response = groq_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": improvement_prompt}],
            temperature=0.3,
            max_tokens=2048
        )

        return {
            "agent_name": agent_config.name,
            "improvement_analysis": response.choices[0].message.content,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/collaborate")
async def agent_collaborate(agents: List[AgentConfig], topic: str):
    """
    Collaborative learning - multiple agents discuss and learn from each other.
    """
    try:
        agent_descriptions = "\n".join([
            f"Agent {i+1}: {agent.name} ({agent.role}) - Goal: {agent.goal}"
            for i, agent in enumerate(agents)
        ])

        collaboration_prompt = f"""You are facilitating a collaborative learning session between the following AI agents:

{agent_descriptions}

Topic for Discussion: {topic}

Please simulate a collaborative discussion where:
1. Each agent contributes their unique perspective
2. Agents build on each other's ideas
3. A consensus or synthesis is reached
4. Each agent learns something new from the others

Format the output as a structured dialogue showing the collaborative learning process."""

        response = groq_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": collaboration_prompt}],
            temperature=0.7,
            max_tokens=3000
        )

        return {
            "topic": topic,
            "agents": [agent.name for agent in agents],
            "collaboration": response.choices[0].message.content,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── WebSocket Endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to AI Startup WebSocket",
            "active_crews": len(active_crews)
        })

        while True:
            data = await websocket.receive_json()

            if data.get("type") == "create_crew":
                # Handle crew creation via WebSocket
                crew_request = CrewRequest(**data["payload"])
                crew = Crew(crew_request)
                active_crews[crew.crew_id] = crew

                await websocket.send_json({
                    "type": "crew_created",
                    "crew_id": crew.crew_id,
                    "message": "Crew created and starting..."
                })

                # Start crew execution
                asyncio.create_task(crew.run())

            elif data.get("type") == "chat":
                # Handle chat via WebSocket
                messages = data.get("messages", [])
                model = data.get("model", DEFAULT_MODEL)

                response = groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048
                )

                await websocket.send_json({
                    "type": "chat_response",
                    "content": response.choices[0].message.content,
                    "model": model
                })

            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        manager.disconnect(websocket)

# ── Pre-built Crew Templates ──────────────────────────────────────────────────

@app.get("/templates")
async def get_templates():
    return {
        "templates": [
            {
                "id": "startup_ideation",
                "name": "Startup Ideation Crew",
                "description": "Generate and validate startup ideas",
                "agents": [
                    {
                        "name": "Market Researcher",
                        "role": "Market Research Specialist",
                        "goal": "Identify market gaps and opportunities",
                        "backstory": "Expert in market analysis with 10+ years experience"
                    },
                    {
                        "name": "Product Strategist",
                        "role": "Product Strategy Expert",
                        "goal": "Define product vision and roadmap",
                        "backstory": "Serial entrepreneur with multiple successful exits"
                    },
                    {
                        "name": "Tech Architect",
                        "role": "Technical Architect",
                        "goal": "Design scalable technical architecture",
                        "backstory": "Former principal engineer at top tech companies"
                    }
                ],
                "tasks": [
                    {
                        "description": "Research current market trends and identify 3 high-potential opportunities",
                        "expected_output": "Market analysis report with opportunities",
                        "agent_name": "Market Researcher"
                    },
                    {
                        "description": "Based on market research, define a compelling product vision and MVP features",
                        "expected_output": "Product vision document with MVP scope",
                        "agent_name": "Product Strategist"
                    },
                    {
                        "description": "Design technical architecture for the MVP including stack recommendations",
                        "expected_output": "Technical architecture document",
                        "agent_name": "Tech Architect"
                    }
                ]
            },
            {
                "id": "code_review",
                "name": "AI Code Review Crew",
                "description": "Automated code review and optimization",
                "agents": [
                    {
                        "name": "Code Reviewer",
                        "role": "Senior Code Reviewer",
                        "goal": "Identify bugs, security issues, and code smells",
                        "backstory": "Staff engineer with expertise in code quality"
                    },
                    {
                        "name": "Performance Optimizer",
                        "role": "Performance Engineer",
                        "goal": "Optimize code for speed and efficiency",
                        "backstory": "Specialist in high-performance computing"
                    },
                    {
                        "name": "Security Auditor",
                        "role": "Security Expert",
                        "goal": "Identify and fix security vulnerabilities",
                        "backstory": "Former security researcher at major tech firm"
                    }
                ],
                "tasks": [
                    {
                        "description": "Review the provided code for bugs, anti-patterns, and style issues",
                        "expected_output": "Code review report with issues found",
                        "agent_name": "Code Reviewer"
                    },
                    {
                        "description": "Analyze code performance and suggest optimizations",
                        "expected_output": "Performance optimization recommendations",
                        "agent_name": "Performance Optimizer"
                    },
                    {
                        "description": "Audit code for security vulnerabilities and suggest fixes",
                        "expected_output": "Security audit report",
                        "agent_name": "Security Auditor"
                    }
                ]
            },
            {
                "id": "content_creation",
                "name": "Content Creation Crew",
                "description": "AI-powered content creation pipeline",
                "agents": [
                    {
                        "name": "Content Strategist",
                        "role": "Content Strategy Expert",
                        "goal": "Develop content strategy and topics",
                        "backstory": "Award-winning content strategist"
                    },
                    {
                        "name": "Copywriter",
                        "role": "Professional Copywriter",
                        "goal": "Write engaging and persuasive content",
                        "backstory": "Published author and top-rated copywriter"
                    },
                    {
                        "name": "SEO Specialist",
                        "role": "SEO Expert",
                        "goal": "Optimize content for search engines",
                        "backstory": "SEO consultant for Fortune 500 companies"
                    }
                ],
                "tasks": [
                    {
                        "description": "Develop a content strategy with 5 topic ideas for the given niche",
                        "expected_output": "Content strategy document",
                        "agent_name": "Content Strategist"
                    },
                    {
                        "description": "Write a compelling blog post based on the top topic",
                        "expected_output": "Complete blog post (1000+ words)",
                        "agent_name": "Copywriter"
                    },
                    {
                        "description": "Optimize the blog post for SEO with keywords and meta descriptions",
                        "expected_output": "SEO-optimized version with metadata",
                        "agent_name": "SEO Specialist"
                    }
                ]
            }
        ]
    }

# ── Run Server ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
