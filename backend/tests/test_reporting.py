from unittest.mock import MagicMock
from backend.evaluation.reporting import ReportingEngine

def test_generate_report() -> None:
    mock_store = MagicMock()
    mock_store.get_history.return_value = [
        {"score": 90, "persona_id": "p1"},
        {"score": 70, "persona_id": "p1"},
        {"score": 50, "persona_id": "p2"}
    ]
    
    engine = ReportingEngine(mock_store)
    report = engine.generate_report("s1")
    
    assert report.total_challenges == 3
    assert report.overall_score == 70 # (90+70+50)/3
    assert len(report.persona_breakdown) == 2
    
    p1_score = next(p for p in report.persona_breakdown if p.persona_id == "p1")
    assert p1_score.average_score == 80 # (90+70)/2
    
    p2_score = next(p for p in report.persona_breakdown if p.persona_id == "p2")
    assert p2_score.average_score == 50

def test_generate_report_empty() -> None:
    mock_store = MagicMock()
    mock_store.get_history.return_value = []
    
    engine = ReportingEngine(mock_store)
    report = engine.generate_report("s1")
    
    assert report.overall_score == 0
    assert report.total_challenges == 0
