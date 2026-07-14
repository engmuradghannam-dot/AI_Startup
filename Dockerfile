# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies + Node.js (for Railway compatibility)
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     curl     ca-certificates     && rm -rf /var/lib/apt/lists/*

# Install Node.js (needed because Railway detects package.json)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&     apt-get install -y nodejs &&     rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/app/ ./app/
COPY backend/tests/ ./tests/

# Copy built frontend static files
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
