"""AI Chat API routes - Uses Unified AI Service (Local LLM first, Groq fallback)."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import httpx
import json

from app.services.unified_ai_service import get_unified_ai_service, UnifiedAIService
from app.services.multi_agent_orchestrator import get_multi_agent_orchestrator, MultiAgentOrchestrator
from app.services.multi_provider_ai import get_multi_provider_service

# Providers this app has a real image payload adapter for (see multi_provider_ai.py).
# Any other active provider gets a text note instead of the raw image, so an
# unsupported model can't crash the request with a "content must be a string" error.
VISION_CAPABLE_PROVIDERS = {"google", "anthropic", "openai"}

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])


# ============================================
# PYDANTIC MODELS
# ============================================

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatAttachment(BaseModel):
    name: str
    content_type: str
    data: str  # plain text, or base64 if is_base64
    is_base64: bool = False


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: bool = False
    agent_mode: Optional[str] = "auto"  # auto, single, multi, swarm
    mode: Optional[str] = None  # alias for agent_mode
    attachment: Optional[ChatAttachment] = None


MAX_ATTACHMENT_CHARS = 15000


def _apply_attachment(messages: List[dict], attachment: Optional[ChatAttachment]) -> List[dict]:
    """Fold an attachment into the last user message so the model can see it."""
    if not attachment or not messages:
        return messages

    last = messages[-1]

    if attachment.content_type.startswith("image/") and attachment.is_base64:
        last["content"] = [
            {"type": "text", "text": last["content"]},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{attachment.content_type};base64,{attachment.data}"},
            },
        ]
        return messages

    text = attachment.data[:MAX_ATTACHMENT_CHARS]
    last["content"] = f"{last['content']}\n\n[Attached file: {attachment.name}]\n{text}"
    return messages


class AgentChatRequest(BaseModel):
    task: str
    agents: Optional[List[str]] = None
    mode: str = "hierarchical"  # sequential, parallel, hierarchical, swarm
    context: Optional[dict] = None


class SkillChatRequest(BaseModel):
    task: str
    skills: List[str]
    context: Optional[dict] = None


class ModelInfoResponse(BaseModel):
    id: str
    name: str
    provider: str
    size: str
    parameters: str
    speed: str
    capabilities: List[str]
    best_for: List[str]
    ram_required_mb: int


# ============================================
# CHAT ENDPOINTS
# ============================================

async def _resolve_messages_and_mode(request: ChatRequest) -> tuple:
    """Apply any attachment and resolve the final agent_mode. Shared by /chat and /chat/stream."""
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    agent_mode = request.mode or request.agent_mode or "auto"

    is_image_attachment = bool(
        request.attachment
        and request.attachment.content_type.startswith("image/")
        and request.attachment.is_base64
    )
    attachment_handled = False

    if is_image_attachment:
        multi = await get_multi_provider_service()
        active_provider = await multi._get_active_provider()
        if active_provider not in VISION_CAPABLE_PROVIDERS:
            # this provider/model can't accept image content - don't risk a 400,
            # just let the model know an image was attached that it can't see
            last = messages[-1]
            last["content"] = (
                f"{last['content']}\n\n"
                f"[The user attached an image ({request.attachment.name}), but the active "
                f"provider ({active_provider or 'none configured'}) doesn't support image "
                f"understanding in this app. Let them know and suggest switching to Google "
                f"Gemini or Anthropic Claude in Settings if they want the image reviewed.]"
            )
            is_image_attachment = False
            attachment_handled = True

    if request.attachment and not attachment_handled:
        # text attachments, or images the active provider can actually accept
        messages = _apply_attachment(messages, request.attachment)

    # Vision content only works through the direct single-LLM path
    if is_image_attachment:
        agent_mode = "single"

    # Auto-detect if multi-agent is needed
    if agent_mode == "auto":
        last_message = messages[-1]["content"] if messages else ""
        # Simple heuristic: long or complex queries get multi-agent
        if len(last_message) > 200 or any(kw in last_message.lower() for kw in [
            "plan", "design", "architecture", "strategy", "analyze", "compare",
            "create", "build", "develop", "implement", "write code", "debug"
        ]):
            agent_mode = "multi"
        else:
            agent_mode = "single"

    return messages, agent_mode


@router.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint - auto-detects complexity and uses appropriate mode."""
    try:
        unified_ai = await get_unified_ai_service()
        orchestrator = await get_multi_agent_orchestrator()

        messages, agent_mode = await _resolve_messages_and_mode(request)

        if agent_mode == "single":
            # Direct LLM call
            result = await unified_ai.chat_completion(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream,
            )

            return {
                "id": f"chat-{os.urandom(4).hex()}",
                "model": result.get("model", request.model or "default"),
                "provider": result.get("provider", "unknown"),
                "source": result.get("source", "unknown"),
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": result["content"]},
                    "finish_reason": "stop"
                }],
                "usage": result.get("usage", {}),
            }

        else:
            # Multi-agent mode
            task = messages[-1]["content"] if messages else ""
            context = {"conversation_history": messages[:-1]}

            mode = "hierarchical" if agent_mode == "multi" else agent_mode
            result = await orchestrator.execute_multi(task, mode=mode, context=context)

            return {
                "id": f"agent-{os.urandom(4).hex()}",
                "model": "multi-agent",
                "mode": result["mode"],
                "agents_used": result["agents_used"],
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": result["final_output"]},
                    "finish_reason": "stop"
                }],
                "agent_trace": [
                    {
                        "agent": t["agent"],
                        "specialty": t.get("specialty", ""),
                        "thought_preview": t["thought"][:200] + "..." if len(t["thought"]) > 200 else t["thought"],
                        "model_used": t.get("model_used", ""),
                        "provider": t.get("provider", ""),
                    }
                    for t in result.get("agent_trace", [])
                ],
                "duration_seconds": result.get("duration_seconds", 0),
            }

    except Exception as e:
        error_msg = str(e)
        if "No AI provider available" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="AI service unavailable. Please activate a provider in Settings or configure Local LLM."
            )
        raise HTTPException(status_code=500, detail=f"Chat error: {error_msg}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming version of /chat - emits Server-Sent Events as the reply is generated.

    Real token-by-token streaming only happens for agent_mode="single" (direct LLM
    call) on providers with an SSE parser (see multi_provider_ai.SSE_COMPATIBLE_PROVIDERS).
    Multi-agent mode runs the normal (blocking) orchestration and streams the final
    result as one chunk, so the client can use the same event-reading code either way.
    """
    from fastapi.responses import StreamingResponse

    async def event_source():
        def sse(payload: dict) -> str:
            return f"data: {json.dumps(payload)}\n\n"

        try:
            unified_ai = await get_unified_ai_service()
            messages, agent_mode = await _resolve_messages_and_mode(request)

            if agent_mode == "single":
                async for event in unified_ai.stream_completion(
                    messages=messages, model=request.model,
                    temperature=request.temperature, max_tokens=request.max_tokens,
                ):
                    if "error" in event:
                        yield sse({"error": event["error"]})
                        return
                    if "delta" in event:
                        yield sse({"delta": event["delta"]})
                    if event.get("done"):
                        yield sse({
                            "done": True,
                            "model": event.get("model"),
                            "provider": event.get("provider"),
                            "source": event.get("provider"),
                            "usage": event.get("usage", {}),
                        })
            else:
                orchestrator = await get_multi_agent_orchestrator()
                task = messages[-1]["content"] if messages else ""
                context = {"conversation_history": messages[:-1]}
                mode = "hierarchical" if agent_mode == "multi" else agent_mode
                result = await orchestrator.execute_multi(task, mode=mode, context=context)
                yield sse({"delta": result["final_output"]})
                yield sse({
                    "done": True,
                    "model": "multi-agent",
                    "provider": "multi-agent",
                    "source": "multi-agent",
                    "usage": {},
                    "agent_trace": [
                        {"agent": t["agent"], "specialty": t.get("specialty", ""), "provider": t.get("provider", "")}
                        for t in result.get("agent_trace", [])
                    ],
                })
        except Exception as e:
            yield sse({"error": str(e)})

    return StreamingResponse(event_source(), media_type="text/event-stream")


@router.post("/agent-chat")
async def agent_chat(request: AgentChatRequest):
    """Execute multi-agent task with specific agents."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        result = await orchestrator.execute_multi(
            task=request.task,
            mode=request.mode,
            agent_names=request.agents,
            context=request.context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent chat error: {str(e)}")


@router.post("/skill-chat")
async def skill_chat(request: SkillChatRequest):
    """Execute task with specific skills."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        result = await orchestrator.execute_with_skills(
            task=request.task,
            skills=request.skills,
            context=request.context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill chat error: {str(e)}")


# ============================================
# MODEL MANAGEMENT
# ============================================

@router.get("/models", response_model=List[ModelInfoResponse])
async def list_models():
    """List all available AI models (local + cloud)."""
    try:
        unified_ai = await get_unified_ai_service()
        models = await unified_ai.get_available_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.post("/models/pull/{model_name}")
async def pull_model(model_name: str):
    """Pull a model to local Ollama."""
    try:
        unified_ai = await get_unified_ai_service()
        result = await unified_ai.pull_local_model(model_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {str(e)}")


# ============================================
# AGENT MANAGEMENT
# ============================================

@router.get("/agents")
async def list_agents():
    """List all available multi-agents."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        return {"agents": orchestrator.list_agents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent info."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        agent = orchestrator.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        return {
            "name": agent.name,
            "specialty": agent.specialty,
            "description": agent.description,
            "skills": agent.skills,
            "model": agent.model,
            "metrics": agent.metrics,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.post("/agents/{agent_name}/execute")
async def execute_agent(agent_name: str, request: dict):
    """Execute a single agent."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        result = await orchestrator.execute_single(
            agent_name=agent_name,
            task=request.get("task", ""),
            context=request.get("context"),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")


@router.post("/agents/clear-memory")
async def clear_all_memory():
    """Clear all agent memories."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        orchestrator.clear_memory()
        return {"status": "success", "message": "All agent memories cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")


@router.post("/agents/{agent_name}/clear-memory")
async def clear_agent_memory(agent_name: str):
    """Clear specific agent memory."""
    try:
        orchestrator = await get_multi_agent_orchestrator()
        orchestrator.clear_memory(agent_name)
        return {"status": "success", "message": f"Memory cleared for agent '{agent_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")


# ============================================
# HEALTH & METRICS
# ============================================

@router.get("/health")
async def ai_health():
    """Check AI service health."""
    try:
        unified_ai = await get_unified_ai_service()
        health = await unified_ai.health_check()
        return health
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "local": {"connected": False},
            "groq": {"available": False},
        }


@router.get("/metrics")
async def ai_metrics():
    """Get AI service usage metrics."""
    try:
        unified_ai = await get_unified_ai_service()
        return unified_ai.get_metrics()
    except Exception as e:
        return {"error": str(e)}
