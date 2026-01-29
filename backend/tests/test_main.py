"""
Tests for main.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check() -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Health check now includes database and redis status
    assert data["status"] == "ok"
    assert "database" in data
    assert "redis" in data
