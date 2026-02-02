"""
SoundTouchBridge - Main FastAPI Application
Iteration 0: Basic setup with /health endpoint
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from cloudtouch.core.config import init_config, get_config
from cloudtouch.db import DeviceRepository
from cloudtouch.settings.repository import SettingsRepository
from cloudtouch.api import devices_router
from cloudtouch.radio.api.routes import router as radio_router
from cloudtouch.settings.routes import router as settings_router
from cloudtouch.core.logging import setup_logging


# Global instances (initialized in lifespan)
device_repo: Optional[DeviceRepository] = None
settings_repo: Optional[SettingsRepository] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    global device_repo, settings_repo

    # Initialize configuration
    init_config()

    # Setup structured logging
    setup_logging()

    logger = logging.getLogger(__name__)
    cfg = get_config()
    logger.info(f"SoundTouchBridge starting on {cfg.host}:{cfg.port}")
    logger.info(f"Database: {cfg.db_path}")
    logger.info(f"Discovery enabled: {cfg.discovery_enabled}")

    # Initialize database
    device_repo = DeviceRepository(cfg.db_path)
    await device_repo.initialize()
    logger.info("Device repository initialized")

    # Initialize settings repository (convert str to Path if needed)
    from pathlib import Path
    db_path = Path(cfg.db_path) if isinstance(cfg.db_path, str) else cfg.db_path
    settings_repo = SettingsRepository(db_path)
    await settings_repo.initialize()
    logger.info("Settings repository initialized")

    yield

    # Shutdown
    if device_repo:
        await device_repo.close()
        logger.info("Device repository closed")

    if settings_repo:
        await settings_repo.close()
        logger.info("Settings repository closed")

    logger.info("SoundTouchBridge shutting down")


# Initialize config before app creation
init_config()

# FastAPI app
app = FastAPI(
    title="SoundTouchBridge",
    version="0.2.0",
    description="Open-Source replacement for Bose SoundTouch cloud features",
    lifespan=lifespan,
)

# CORS middleware for Web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: configure properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(devices_router)
app.include_router(radio_router)
app.include_router(settings_router)


# Health endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    cfg = get_config()
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": "0.2.0",
            "config": {
                "discovery_enabled": cfg.discovery_enabled,
                "db_path": cfg.db_path,
            },
        },
    )


# Static files (frontend)
# Development: ../../frontend/dist
# Production: frontend/dist (copied during Docker build)
static_dir = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if not static_dir.exists():
    # Fallback for Docker/production deployment
    static_dir = Path(__file__).parent.parent / "frontend" / "dist"

if static_dir.exists():
    from fastapi.responses import FileResponse

    # Serve static assets (CSS, JS, images)
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    # Catch-all route for SPA (React Router) - must come AFTER API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve index.html for all non-API routes (SPA support)."""
        # If requesting a static file that exists, serve it
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html (React Router handles the rest)
        return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn

    cfg = get_config()
    uvicorn.run(
        "main:app",
        host=cfg.host,
        port=cfg.port,
        log_level=cfg.log_level.lower(),
        reload=True,
    )
