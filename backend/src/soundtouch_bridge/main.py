"""
SoundTouchBridge - Main FastAPI Application
Iteration 0: Basic setup with /health endpoint
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from soundtouch_bridge.core.config import init_config, get_config
from soundtouch_bridge.db import DeviceRepository
from soundtouch_bridge.api import devices_router
from soundtouch_bridge.radio.api.routes import router as radio_router
from soundtouch_bridge.core.logging import setup_logging


# Global instances
device_repo: DeviceRepository = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    global device_repo
    
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
    
    yield
    
    # Shutdown
    if device_repo:
        await device_repo.close()
        logger.info("Device repository closed")
    
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
from pathlib import Path
from fastapi.staticfiles import StaticFiles

static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


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
