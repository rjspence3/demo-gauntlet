"""
Tests for reporting_api.
"""
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.evaluation.router.SessionStore")
@patch("backend.evaluation.router.ReportingEngine")
def test_get_report(mock_engine_cls: MagicMock, mock_store_cls: MagicMock) -> None:
    """Test report endpoint."""
    mock_engine = mock_engine_cls.return_value
    mock_report = MagicMock()
    mock_report.overall_score = 85
    mock_report.persona_breakdown = []
    mock_report.total_challenges = 5
    mock_report.strengths = ["S1"]
    mock_report.weaknesses = ["W1"]
    
    # Mock asdict to return a dict, since the real asdict works on dataclasses
    # but our mock_report is a MagicMock.
    # Actually, let's just return a real SessionReport object from the mock engine
    from backend.evaluation.reporting import SessionReport
    mock_engine.generate_report.return_value = SessionReport(
        overall_score=85,
        persona_breakdown=[],
        total_challenges=5,
        strengths=["S1"],
        weaknesses=["W1"],
        slide_breakdown={}
    )
    
    response = client.get("/evaluation/report/s1")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 85
    assert data["total_challenges"] == 5
