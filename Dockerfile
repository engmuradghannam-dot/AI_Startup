# Build v2.4 - Railway Compatible with $PORT + Cache Busting
# ============================================
# AI Startup - Railway Deployment
# Multi-Stage Build with Cache Invalidation
# ============================================

# -------- Stage 1: Frontend Builder --------
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Cache busting - forces rebuild on every deploy
ARG CACHEBUST=1
ENV CACHEBUST=${CACHEBUST}

# Copy and install frontend deps
COPY frontend/package.json ./
COPY frontend/package-lock.json* ./
RUN npm install --prefer-offline --no-audit --no-fund

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Verify build output exists
RUN ls -la /app/frontend/dist/ && echo "✅ Frontend build verified"

# -------- Stage 2: Python Backend --------
FROM python:3.11-slim

WORKDIR /app

# Cache busting - forces rebuild on every deploy
ARG CACHEBUST=1
ENV CACHEBUST=${CACHEBUST}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app/ ./app/
COPY backend/tests/ ./tests/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Verify frontend files copied
RUN ls -la /app/frontend_dist/ && echo "✅ Frontend dist copied to backend"

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MONGODB_URI=mongodb+srv://engmuradghannam_db_user:IWqsSLrcTgnwdgpD@cluster0.ouxl0wd.mongodb.net/ai_startup?retryWrites=true&w=majority
ENV DATABASE_NAME=ai_startup
ENV ENVIRONMENT=production
# Accept all API keys from Railway env vars
ARG GROQ_API_KEY=""
ARG OPENAI_API_KEY=""
ARG ANTHROPIC_API_KEY=""
ARG GOOGLE_API_KEY=""
ARG COHERE_API_KEY=""
ARG MISTRAL_API_KEY=""
ARG XAI_API_KEY=""
ARG KIMI_API_KEY=""
ARG MOONSHOT_API_KEY=""

ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV COHERE_API_KEY=${COHERE_API_KEY}
ENV MISTRAL_API_KEY=${MISTRAL_API_KEY}
ENV XAI_API_KEY=${XAI_API_KEY}
ENV KIMI_API_KEY=${KIMI_API_KEY}
ENV MOONSHOT_API_KEY=${MOONSHOT_API_KEY}
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (Railway sets $PORT)
EXPOSE ${PORT:-8080}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + str(__import__('os').environ.get('PORT', '8080')) + '/health/')" || exit 1

# Start command - MUST use $PORT for Railway
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
