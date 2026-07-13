# AI Startup - Multi-Agent System

A powerful AI startup framework built with FastAPI, React, and Groq API integration. Features a multi-agent orchestration system with 10 Claude Fable 5 native skills.

## Features

- **Multi-Agent Orchestration**: Create and manage teams of AI agents that collaborate on complex tasks
- **Groq API Integration**: Leverage high-performance LLMs including Llama 3.3 70B, Llama 4 Scout, Compound Beta, and more
- **Real-time Communication**: WebSocket support for live agent status updates
- **10 Fable 5 Skills**: Built-in agent skills for optimal performance
- **Pre-built Templates**: Startup Ideation, Code Review, and Content Creation crews
- **Self-Improving Code**: Agents can analyze and optimize their own configurations
- **Collaborative Learning**: Agents share knowledge and learn from each other

## Tech Stack

| Technology | Usage |
|------------|-------|
| Python/FastAPI | Backend API |
| React + Vite | Frontend |
| Groq API | LLM Integration |
| Redis | Caching & Message Queue |
| Docker | Containerization |

## Quick Start

### Using Docker Compose

```bash
# Clone and navigate
cd ai_startup

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 10 Fable 5 Skills

1. **Act When Ready** - Stop over-planning, take action when sufficient
2. **Autonomous Continuation** - Run to completion without human intervention
3. **Effort Calibrator** - Optimize effort vs latency/cost trade-offs
4. **Grounded Progress** - Verifiable progress reports with evidence
5. **Markdown Memory** - Persistent lesson memory across sessions
6. **No Gold-Plating** - Minimal changes, no feature creep
7. **Re-grounding Summary** - Reports readable without context
8. **Scope Guard** - Prevent unrequested actions
9. **Skill Refactorer** - Migrate skills for Fable 5 optimization
10. **Subagent Orchestration** - Parallel agent coordination

## API Endpoints

- `GET /` - System status and info
- `GET /models` - Available Groq models
- `POST /chat` - Chat with AI models
- `POST /crew/create` - Create and launch a crew
- `GET /crew/{id}/status` - Check crew status
- `GET /crews` - List all crews
- `POST /agent/self-improve` - Self-improvement analysis
- `POST /agent/collaborate` - Collaborative learning
- `GET /templates` - Pre-built crew templates
- `WS /ws` - WebSocket for real-time updates

## Environment Variables

```env
GROQ_API_KEY=your_groq_api_key
REDIS_URL=redis://localhost:6379
VITE_API_URL=http://localhost:8000
```

## License

MIT
