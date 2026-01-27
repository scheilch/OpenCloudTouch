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

from backend.config import init_config, get_config


# Logging setup
def setup_logging():
    """Configure logging for the application."""
    cfg = get_config()
    logging.basicConfig(
        level=cfg.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger = logging.getLogger(__name__)
    cfg = get_config()
    logger.info(f"SoundTouchBridge starting on {cfg.host}:{cfg.port}")
    logger.info(f"Database: {cfg.db_path}")
    logger.info(f"Discovery enabled: {cfg.discovery_enabled}")
    
    # Startup logic hier (z.B. DB init, discovery start)
    yield
    
    # Shutdown logic hier
    logger.info("SoundTouchBridge shutting down")


# Initialize config before app creation
init_config()
setup_logging()

# FastAPI app
app = FastAPI(
    title="SoundTouchBridge",
    version="0.1.0",
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


# Health endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    cfg = get_config()
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": "0.1.0",
            "config": {
                "discovery_enabled": cfg.discovery_enabled,
                "db_path": cfg.db_path,
            },
        },
    )


# Static files (frontend) - will be built in later iterations
# Commented out for now - no frontend build yet
# static_dir = Path(__file__).parent.parent / "frontend" / "dist"
# if static_dir.exists():
#     app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


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
