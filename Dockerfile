# ============================================
# AI Startup - Multi-Stage Docker Build
# Railway Compatible
# ============================================

# -------- Stage 1: Frontend Builder --------
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy package files first (for caching)
COPY frontend/package*.json ./
RUN npm ci --only=production 2>/dev/null || npm install

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# -------- Stage 2: Python Backend --------
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libffi-dev     libssl-dev     && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app/ ./app/
COPY backend/tests/ ./tests/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Railway uses PORT env var - bind to 0.0.0.0
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Start command - bind to 0.0.0.0 for Railway
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
