# syntax=docker/dockerfile:1

# ============================================================
# Multi-stage build for SoundTouchBridge
# Supports amd64 and arm64
# ============================================================

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend + Runtime
FROM python:3.11-slim AS backend

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy E2E demo scripts
COPY e2e/ ./e2e/

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create data directory
RUN mkdir -p /data

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7777/health')" || exit 1

# Expose port
EXPOSE 7777

# Run as non-root user
RUN useradd -m -u 1000 stb && chown -R stb:stb /app /data
USER stb

# Environment defaults
ENV STB_HOST=0.0.0.0
ENV STB_PORT=7777
ENV STB_DB_PATH=/data/stb.db
ENV STB_LOG_LEVEL=INFO

# Set Python path
ENV PYTHONPATH=/app

# Start application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7777"]
