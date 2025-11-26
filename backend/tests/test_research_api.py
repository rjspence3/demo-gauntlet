from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_generate_research_endpoint() -> None:
    """Test the research generation endpoint."""
    response = client.post("/research/generate/test-session")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert "competitor_insights" in data
