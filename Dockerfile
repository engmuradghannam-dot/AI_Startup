# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend with Node.js
FROM python:3.11

WORKDIR /app

# Install Node.js 20 from NodeSource (using apt-get after adding repo)
RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates     gnupg     && mkdir -p /etc/apt/keyrings     && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg     && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list     && apt-get update     && apt-get install -y nodejs     && rm -rf /var/lib/apt/lists/*

# Verify node is installed
RUN node --version && npm --version

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
