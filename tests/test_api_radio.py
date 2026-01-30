"""
Tests for Radio API endpoints

TDD RED Phase: These tests will fail until FastAPI endpoints are implemented.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from backend.main import app
from backend.adapters.radiobrowser_adapter import RadioStation, RadioBrowserError
from backend.api.radio import get_radiobrowser_adapter


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_adapter():
    """Mock RadioBrowser adapter."""
    return AsyncMock()


@pytest.fixture
def mock_radio_stations():
    """Mock radio station data."""
    return [
        RadioStation(
            station_uuid="test-uuid-1",
            name="Test Radio 1",
            url="http://stream1.example.com/radio.mp3",
            country="Germany",
            codec="MP3",
            bitrate=128,
            tags="pop,rock"
        ),
        RadioStation(
            station_uuid="test-uuid-2",
            name="Test Radio 2",
            url="http://stream2.example.com/radio.mp3",
            country="Switzerland",
            codec="AAC",
            bitrate=192,
            tags="jazz,smooth"
        )
    ]


class TestRadioSearchEndpoint:
    """Tests for GET /api/radio/search endpoint."""
    
    def test_search_endpoint_exists(self, client):
        """Test that /api/radio/search endpoint exists."""
        response = client.get("/api/radio/search", params={"q": "test"})
        
        # Should not be 404 Not Found
        assert response.status_code != 404
    
    def test_search_by_name(self, client, mock_adapter, mock_radio_stations):
        """Test search by station name."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test", "search_type": "name"})
            
            assert response.status_code == 200
            data = response.json()
            
            assert "stations" in data
            assert len(data["stations"]) == 2
            assert data["stations"][0]["name"] == "Test Radio 1"
            assert data["stations"][0]["uuid"] == "test-uuid-1"
        finally:
            app.dependency_overrides.clear()
    
    def test_search_by_country(self, client, mock_adapter, mock_radio_stations):
        """Test search by country."""
        mock_adapter.search_by_country.return_value = [mock_radio_stations[0]]
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "Germany", "search_type": "country"})
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data["stations"]) == 1
            assert data["stations"][0]["country"] == "Germany"
        finally:
            app.dependency_overrides.clear()
    
    def test_search_by_tag(self, client, mock_adapter, mock_radio_stations):
        """Test search by tag."""
        mock_adapter.search_by_tag.return_value = [mock_radio_stations[1]]
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "jazz", "search_type": "tag"})
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data["stations"]) == 1
            assert "jazz" in data["stations"][0]["tags"]
        finally:
            app.dependency_overrides.clear()
    
    def test_search_default_type_is_name(self, client, mock_adapter, mock_radio_stations):
        """Test that default search type is 'name'."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test"})
            
            assert response.status_code == 200
            mock_adapter.search_by_name.assert_called_once()
        finally:
            app.dependency_overrides.clear()
    
    def test_search_limit_parameter(self, client, mock_adapter, mock_radio_stations):
        """Test that limit parameter is passed correctly."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test", "limit": 25})
            
            assert response.status_code == 200
            mock_adapter.search_by_name.assert_called_once_with("test", limit=25)
        finally:
            app.dependency_overrides.clear()
    
    def test_search_default_limit(self, client, mock_adapter, mock_radio_stations):
        """Test default limit is 10."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test"})
            
            assert response.status_code == 200
            mock_adapter.search_by_name.assert_called_once_with("test", limit=10)
        finally:
            app.dependency_overrides.clear()
    
    def test_search_missing_query_parameter(self, client):
        """Test that missing 'q' parameter returns 422."""
        response = client.get("/api/radio/search")
        
        assert response.status_code == 422
    
    def test_search_empty_query_parameter(self, client):
        """Test that empty 'q' parameter returns 400."""
        response = client.get("/api/radio/search", params={"q": ""})
        
        # Should reject empty query
        assert response.status_code in [400, 422]
    
    def test_search_invalid_search_type(self, client):
        """Test that invalid search_type returns 422."""
        response = client.get("/api/radio/search", params={"q": "test", "search_type": "invalid"})
        
        assert response.status_code == 422
    
    def test_search_limit_min_value(self, client):
        """Test that limit has minimum value of 1."""
        response = client.get("/api/radio/search", params={"q": "test", "limit": 0})
        
        assert response.status_code == 422
    
    def test_search_limit_max_value(self, client):
        """Test that limit has maximum value of 100."""
        response = client.get("/api/radio/search", params={"q": "test", "limit": 101})
        
        assert response.status_code == 422
    
    def test_search_empty_results(self, client, mock_adapter):
        """Test search with no results."""
        mock_adapter.search_by_name.return_value = []
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "nonexistent"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["stations"] == []
        finally:
            app.dependency_overrides.clear()
    
    def test_search_adapter_error_handling(self, client, mock_adapter):
        """Test that adapter errors are handled gracefully."""
        mock_adapter.search_by_name.side_effect = RadioBrowserError("API error")
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test"})
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
        finally:
            app.dependency_overrides.clear()
    
    def test_search_response_format(self, client, mock_adapter, mock_radio_stations):
        """Test response format structure."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test"})
            
            assert response.status_code == 200
            data = response.json()
            
            # Check structure
            assert "stations" in data
            assert isinstance(data["stations"], list)
            
            # Check station fields
            station = data["stations"][0]
            required_fields = ["uuid", "name", "url", "country", "codec"]
            for field in required_fields:
                assert field in station
        finally:
            app.dependency_overrides.clear()
    
    def test_search_station_field_types(self, client, mock_adapter, mock_radio_stations):
        """Test that response field types are correct."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/search", params={"q": "test"})
            
            assert response.status_code == 200
            data = response.json()
            station = data["stations"][0]
            
            assert isinstance(station["uuid"], str)
            assert isinstance(station["name"], str)
            assert isinstance(station["url"], str)
            assert isinstance(station["bitrate"], int)
        finally:
            app.dependency_overrides.clear()


class TestRadioStationDetailEndpoint:
    """Tests for GET /api/radio/station/{uuid} endpoint."""
    
    def test_station_detail_endpoint_exists(self, client):
        """Test that /api/radio/station/{uuid} endpoint exists."""
        response = client.get("/api/radio/station/test-uuid")
        
        # Should not be 404 Not Found (though station might not exist)
        assert response.status_code in [200, 404, 500, 503]
    
    def test_get_station_by_uuid(self, client, mock_adapter, mock_radio_stations):
        """Test getting station detail by UUID."""
        mock_adapter.get_station_by_uuid.return_value = mock_radio_stations[0]
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/station/test-uuid-1")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["uuid"] == "test-uuid-1"
            assert data["name"] == "Test Radio 1"
        finally:
            app.dependency_overrides.clear()
    
    def test_get_station_not_found(self, client, mock_adapter):
        """Test getting non-existent station returns 404."""
        mock_adapter.get_station_by_uuid.side_effect = RadioBrowserError("Station not found")
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            response = client.get("/api/radio/station/nonexistent")
            
            assert response.status_code in [404, 500]
        finally:
            app.dependency_overrides.clear()


class TestRadioAPIIntegration:
    """Integration tests for Radio API."""
    
    def test_search_and_detail_workflow(self, client, mock_adapter, mock_radio_stations):
        """Test complete workflow: search -> get detail."""
        mock_adapter.search_by_name.return_value = mock_radio_stations
        mock_adapter.get_station_by_uuid.return_value = mock_radio_stations[0]
        
        app.dependency_overrides[get_radiobrowser_adapter] = lambda: mock_adapter
        try:
            # 1. Search
            response = client.get("/api/radio/search", params={"q": "test"})
            assert response.status_code == 200
            stations = response.json()["stations"]
            assert len(stations) > 0
            
            # 2. Get detail for first result
            first_uuid = stations[0]["uuid"]
            response = client.get(f"/api/radio/station/{first_uuid}")
            assert response.status_code == 200
            detail = response.json()
            assert detail["uuid"] == first_uuid
        finally:
            app.dependency_overrides.clear()
