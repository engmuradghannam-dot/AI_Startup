# AI Startup - Multi-Agent System v2.0.0

A powerful multi-agent AI system with 25 integrated skills, Groq API integration, auto-scaling, and collaborative agent orchestration.

## Features

- **25 Integrated Skills** (10 Fable 5 + 15 Advanced)
- **Multi-Agent Orchestration** with load balancing
- **Auto-Scaling** up to 100,000 agents
- **Groq API Integration** with model selection
- **Real-time Monitoring** and performance tracking
- **Knowledge Graph** for interconnected learning
- **Security Guard** for data protection
- **Cost Optimization** with budget management
- **Code Evolution** for self-improving code
- **Multi-Modal Processing** (text, image, audio)
- **Feedback Loop** for continuous learning

## Architecture

```
Frontend (React + Tailwind)
    |
Backend (FastAPI)
    |
Services Layer (15 Services)
    |
Models (Beanie + MongoDB)
    |
Groq API
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Groq API Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/engmuradghannam-dot/AI_Startup.git
cd AI_Startup
```

2. Create environment file:
```bash
cp backend/.env.example backend/.env
```

3. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_key_here
```

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090

## API Endpoints

### Agents
- `POST /agents/` - Create agent
- `GET /agents/` - List agents
- `GET /agents/{id}` - Get agent
- `PUT /agents/{id}` - Update agent
- `DELETE /agents/{id}` - Delete agent
- `POST /agents/{id}/clone` - Clone agent
- `POST /agents/{id}/execute` - Execute task
- `GET /agents/scaling/metrics` - Scaling metrics
- `POST /agents/scaling/scale-up` - Manual scale up

### Skills
- `POST /skills/` - Create skill
- `GET /skills/` - List skills
- `GET /skills/{id}` - Get skill
- `PUT /skills/{id}` - Update skill
- `DELETE /skills/{id}` - Delete skill
- `POST /skills/{id}/execute` - Execute skill
- `GET /skills/categories/summary` - Categories summary

### Training
- `POST /training/datasets` - Create dataset
- `GET /training/datasets` - List datasets
- `POST /training/feedback` - Submit feedback
- `POST /training/feedback/process` - Process feedback
- `GET /training/feedback/stats` - Feedback stats
- `GET /training/memory/{agent_id}` - Agent memory
- `GET /training/knowledge-graph/{agent_id}` - Knowledge graph

### Health
- `GET /health/` - Health check
- `GET /health/metrics` - Performance metrics
- `GET /health/costs` - Cost report
- `GET /health/security` - Security report
- `GET /health/alerts` - Active alerts

## Skills Catalog

### Fable 5 Skills (Core)
1. **Act When Ready** - Prevent over-planning
2. **Autonomous Continuation** - Unattended execution
3. **Effort Calibrator** - Appropriate effort per task
4. **No Gold Plating** - Minimal focused changes
5. **Grounded Progress** - Evidence-based reporting
6. **Scope Guard** - Maintain clear boundaries
7. **Subagent Orchestration** - Parallel delegation
8. **Markdown Memory** - File-based lesson memory
9. **Skill Refactorer** - Meta-skill for improvement
10. **Regrounding Summary** - Newcomer-friendly reports

### Advanced Skills
11. **Auto-Scaling** - Dynamic agent creation
12. **Load Balancer** - Task distribution
13. **Error Recovery** - Self-healing failures
14. **Code Evolver** - Auto-improve code
15. **Model Selector** - Optimal model choice
16. **Context Optimizer** - Token efficiency
17. **Multi-Modal** - Image/audio/text processing
18. **Collaboration** - Multi-agent teamwork
19. **Security Guard** - Data protection
20. **Performance Monitor** - Real-time metrics
21. **Data Pipeline** - Data processing
22. **Feedback Loop** - Continuous learning
23. **Deployment Manager** - Safe deployments
24. **Cost Optimizer** - Budget management
25. **Knowledge Graph** - Interconnected learning

## Agent Roles

- General
- Marketing
- Legal
- Finance
- HR
- Healthcare
- Developer
- Designer
- Analyst
- Manager
- Researcher
- Security
- DevOps
- Data Scientist

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
pytest tests/ -v
```

## Scaling Performance

| Agents | Estimated Time | Recommendation |
|--------|---------------|----------------|
| 1-10 | Instant | For testing |
| 10-100 | 2-5 min | Small projects |
| 100-1,000 | 10-30 min | Medium projects |
| 1,000-10,000 | 1-3 hours | Needs Groq Batch API |
| 10,000-100,000 | 3-12 hours | Needs distributed servers |

## License

MIT License

## Author

engmuradghannam-dot
