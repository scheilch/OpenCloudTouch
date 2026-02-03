"""Integration tests for Settings API routes."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from cloudtouch.main import app
from cloudtouch.settings.routes import get_settings_repo


@pytest.fixture
def mock_settings_repo():
    """Mock settings repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def client(mock_settings_repo):
    """FastAPI test client with dependency override."""
    app.dependency_overrides[get_settings_repo] = lambda: mock_settings_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestManualIPsEndpoints:
    """Tests for manual IPs API endpoints."""

    def test_get_manual_ips_empty(self, client, mock_settings_repo):
        """Test GET /api/settings/manual-ips with no IPs."""
        # Arrange
        mock_settings_repo.get_manual_ips = AsyncMock(return_value=[])

        # Act
        response = client.get("/api/settings/manual-ips")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == {"ips": []}

    def test_get_manual_ips_with_data(self, client, mock_settings_repo):
        """Test GET /api/settings/manual-ips with existing IPs."""
        # Arrange
        test_ips = ["192.168.1.10", "192.168.1.20", "10.0.0.5"]
        mock_settings_repo.get_manual_ips = AsyncMock(return_value=test_ips)

        # Act
        response = client.get("/api/settings/manual-ips")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == {"ips": test_ips}

    def test_delete_manual_ip_success(self, client, mock_settings_repo):
        """Test DELETE /api/settings/manual-ips/{ip} with existing IP."""
        # Arrange
        ip_to_delete = "192.168.1.10"
        mock_settings_repo.remove_manual_ip = AsyncMock()

        # Act
        response = client.delete(f"/api/settings/manual-ips/{ip_to_delete}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == {"message": "IP removed successfully", "ip": ip_to_delete}
        mock_settings_repo.remove_manual_ip.assert_awaited_once_with(ip_to_delete)

    def test_delete_manual_ip_not_found(self, client, mock_settings_repo):
        """Test DELETE /api/settings/manual-ips/{ip} with non-existent IP."""
        # Arrange
        ip_to_delete = "192.168.1.99"
        mock_settings_repo.remove_manual_ip = AsyncMock()  # Does not raise

        # Act
        response = client.delete(f"/api/settings/manual-ips/{ip_to_delete}")

        # Assert
        # Should succeed even if IP doesn't exist (idempotent)
        assert response.status_code == 200
        data = response.json()
        assert data == {"message": "IP removed successfully", "ip": ip_to_delete}
