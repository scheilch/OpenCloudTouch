"""Integration tests for Settings API routes."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from opencloudtouch.main import app
from opencloudtouch.settings.routes import get_settings_repo


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

    def test_add_manual_ips_success(self, client, mock_settings_repo):
        """Test POST /api/settings/manual-ips with valid IPs."""
        # Arrange
        new_ips = ["192.168.1.50", "10.0.0.100"]
        mock_settings_repo.add_manual_ip = AsyncMock()

        # Act
        response = client.post("/api/settings/manual-ips", json={"ips": new_ips})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == {"ips": new_ips}
        # Should be called twice (once per IP)
        assert mock_settings_repo.add_manual_ip.await_count == 2

    def test_add_manual_ips_invalid_ip_format(self, client, mock_settings_repo):
        """Test POST /api/settings/manual-ips with invalid IP format."""
        # Arrange
        invalid_ips = ["192.168.1.999", "not-an-ip", "10.0.0.1"]
        mock_settings_repo.add_manual_ip = AsyncMock(
            side_effect=ValueError("Invalid IP address")
        )

        # Act
        response = client.post("/api/settings/manual-ips", json={"ips": invalid_ips})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Invalid IP address" in data["detail"]

    def test_add_manual_ips_empty_list(self, client, mock_settings_repo):
        """Test POST /api/settings/manual-ips with empty list."""
        # Arrange
        mock_settings_repo.add_manual_ip = AsyncMock()

        # Act
        response = client.post("/api/settings/manual-ips", json={"ips": []})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == {"ips": []}
        # Should not call add_manual_ip for empty list
        mock_settings_repo.add_manual_ip.assert_not_awaited()

    def test_add_manual_ips_rollback_on_partial_failure(
        self, client, mock_settings_repo
    ):
        """Test that partial failures trigger rollback of added IPs."""
        # Arrange
        test_ips = ["192.168.1.10", "INVALID", "192.168.1.20"]

        # First IP succeeds, second fails, third not reached
        side_effects = [
            None,  # First IP succeeds
            ValueError("Invalid IP address"),  # Second IP fails
        ]
        mock_settings_repo.add_manual_ip = AsyncMock(side_effect=side_effects)
        mock_settings_repo.remove_manual_ip = AsyncMock()

        # Act
        response = client.post("/api/settings/manual-ips", json={"ips": test_ips})

        # Assert
        assert response.status_code == 400
        # Should attempt rollback for ALL IPs in request (implementation detail)
        # The code rolls back by iterating over request.ips, not tracking which succeeded
        assert mock_settings_repo.remove_manual_ip.await_count == 3
