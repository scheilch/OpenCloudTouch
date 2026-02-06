# syntax=docker/dockerfile:1

# ============================================================
# Multi-stage build for OpenCloudTouch
# Supports amd64 and arm64
# ============================================================

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY apps/frontend/package*.json ./
RUN npm ci

COPY apps/frontend/ ./
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
COPY apps/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source (as package)
COPY apps/backend/src/opencloudtouch ./opencloudtouch

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
RUN useradd -m -u 1000 oct && chown -R oct:oct /app /data
USER oct

# Environment defaults
ENV OCT_HOST=0.0.0.0
ENV OCT_PORT=7777
ENV OCT_DB_PATH=/data/oct.db
ENV OCT_LOG_LEVEL=INFO

# Set Python path for package
ENV PYTHONPATH=/app

# Start application using module entry point
CMD ["python", "-m", "opencloudtouch"]
