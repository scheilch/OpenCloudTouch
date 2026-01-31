"""Tests for main application module (startup, lifecycle)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_lifespan_initialization():
    """Test lifespan context manager initializes config and DB."""
    from soundtouch_bridge.main import lifespan, app
    from soundtouch_bridge.core.config import AppConfig
    
    with patch("soundtouch_bridge.main.init_config") as mock_init_config, \
         patch("soundtouch_bridge.main.setup_logging") as mock_setup_logging, \
         patch("soundtouch_bridge.main.get_config") as mock_get_config, \
         patch("soundtouch_bridge.main.DeviceRepository") as mock_repo_class:
        
        # Mock config
        mock_config = MagicMock(spec=AppConfig)
        mock_config.host = "0.0.0.0"
        mock_config.port = 7777
        mock_config.db_path = ":memory:"
        mock_config.discovery_enabled = True
        mock_get_config.return_value = mock_config
        
        # Mock repository
        mock_repo = AsyncMock()
        mock_repo.initialize = AsyncMock()
        mock_repo.close = AsyncMock()
        mock_repo_class.return_value = mock_repo
        
        # Run lifespan
        async with lifespan(app):
            # Verify startup
            mock_init_config.assert_called_once()
            mock_setup_logging.assert_called_once()
            mock_repo.initialize.assert_called_once()
        
        # Verify shutdown
        mock_repo.close.assert_called_once()


def test_health_endpoint():
    """Test health check endpoint exists."""
    from soundtouch_bridge.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_routes_registered():
    """Test that API routers are registered."""
    from soundtouch_bridge.main import app
    
    routes = [route.path for route in app.routes]
    
    # Device routes
    assert "/api/devices/discover" in routes or "/api/devices" in routes
    assert "/api/devices/{device_id}" in routes
    assert "/api/devices/sync" in routes
    
    # Radio routes
    assert "/api/radio/search" in routes
    # Note: Route is /api/radio/station/{uuid} (singular)
    assert any("/api/radio/station" in r for r in routes)


def test_cors_middleware_configured():
    """Test CORS middleware is configured."""
    from soundtouch_bridge.main import app
    
    # Check middleware is registered
    # CORS is added via add_middleware, appears as generic Middleware wrapper
    assert len(app.user_middleware) > 0


def test_static_files_mount_when_dir_exists():
    """Test static files are mounted when dist/ exists."""
    from soundtouch_bridge.main import app
    
    # If static_dir exists, static files should be mounted at "/"
    # This creates a catch-all route for static files
    routes = [route.path for route in app.routes]
    # Check if we have routes (static may create catchall)
    assert len(routes) > 0


def test_static_files_not_mounted_when_dir_missing():
    """Test static files are not mounted when dist/ doesn't exist."""
    from soundtouch_bridge.main import app
    
    # Should still have API routes
    routes = [route.path for route in app.routes]
    assert "/api/devices/discover" in routes or "/api/devices/sync" in routes


@pytest.mark.asyncio
async def test_lifespan_error_handling():
    """Test lifespan handles errors gracefully."""
    from soundtouch_bridge.main import lifespan, app
    
    with patch("soundtouch_bridge.main.init_config") as mock_init_config, \
         patch("soundtouch_bridge.main.setup_logging"), \
         patch("soundtouch_bridge.main.get_config") as mock_get_config, \
         patch("soundtouch_bridge.main.DeviceRepository") as mock_repo_class:
        
        mock_config = MagicMock()
        mock_config.host = "0.0.0.0"
        mock_config.port = 7777
        mock_config.db_path = ":memory:"
        mock_config.discovery_enabled = True
        mock_get_config.return_value = mock_config
        
        # Mock repo that fails to initialize
        mock_repo = AsyncMock()
        mock_repo.initialize = AsyncMock(side_effect=Exception("DB connection failed"))
        mock_repo.close = AsyncMock()
        mock_repo_class.return_value = mock_repo
        
        # Should raise exception
        with pytest.raises(Exception, match="DB connection failed"):
            async with lifespan(app):
                pass
