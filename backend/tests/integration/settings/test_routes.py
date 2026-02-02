"""Integration tests for Settings API routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

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

    def test_post_manual_ip_success(self, client, mock_settings_repo):
        """Test POST /api/settings/manual-ips/add with valid IP."""
        # Arrange
        ip_to_add = "192.168.1.10"
        mock_settings_repo.add_manual_ip = AsyncMock()

        # Act
        response = client.post(
            "/api/settings/manual-ips/add", json={"ip": ip_to_add}
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data == {"message": "IP added successfully", "ip": ip_to_add}
        mock_settings_repo.add_manual_ip.assert_awaited_once_with(ip_to_add)

    def test_post_manual_ip_invalid_format(self, client, mock_settings_repo):
        """Test POST /api/settings/manual-ips/add with invalid IP format."""
        # Arrange
        invalid_ip = "999.999.999.999"
        mock_settings_repo.add_manual_ip = AsyncMock(
            side_effect=ValueError(f"Invalid IP address: {invalid_ip}")
        )

        # Act
        response = client.post(
            "/api/settings/manual-ips/add", json={"ip": invalid_ip}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Invalid IP address" in data["detail"]

    def test_post_manual_ip_duplicate(self, client, mock_settings_repo):
        """Test POST /api/settings/manual-ips/add with duplicate IP."""
        # Arrange
        duplicate_ip = "192.168.1.10"
        mock_settings_repo.add_manual_ip = AsyncMock(
            side_effect=ValueError(f"IP address already exists: {duplicate_ip}")
        )

        # Act
        response = client.post(
            "/api/settings/manual-ips/add", json={"ip": duplicate_ip}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"]

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
        mock_settings_repo.remove_manual_ip.assert_awaited_once_with(
            ip_to_delete
        )

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
