"""
Tests for summarizer.
"""
from unittest.mock import MagicMock
from backend.research.summarizer import summarize_research
from backend.research.client import SearchResult

def test_summarize_research() -> None:
    """Test summarizing research results."""
    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = {
        "competitor_insights": ["Insight 1"],
        "cost_benchmarks": ["Cost 1"],
        "compliance_notes": ["Note 1"],
        "implementation_risks": ["Risk 1"]
    }

    results = [
        SearchResult(title="T1", url="U1", snippet="S1", source="Src1")
    ]

    dossier = summarize_research("Session1", results, mock_llm)

    assert dossier.session_id == "Session1"
    assert "Insight 1" in dossier.competitor_insights
    assert "U1" in dossier.sources
    mock_llm.complete_structured.assert_called_once()
