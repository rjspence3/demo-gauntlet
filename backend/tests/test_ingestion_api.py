from typing import Any
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.ingestion.router.os.path.exists")
@patch("backend.ingestion.router.os.listdir")
@patch("backend.ingestion.router.extract_from_file")
def test_get_slides(mock_extract: Any, mock_listdir: Any, mock_exists: Any) -> None:
    """Test retrieving slides."""
    mock_exists.return_value = True
    mock_listdir.return_value = ["deck.pdf"]
    
    mock_slide = MagicMock()
    mock_slide.index = 0
    mock_slide.title = "Slide 1"
    mock_slide.text = "Content"
    # asdict will be called on this, so we need to make it behave like a dataclass or mock asdict
    # easier to just mock the return of extract_from_file to return objects that asdict works on
    # or better, mock extract_from_file to return real Slide objects
    from backend.models.core import Slide
    mock_extract.return_value = [
        Slide(index=0, title="S1", text="T1", notes="N1", tags=[])
    ]
    
    response = client.get("/ingestion/session/test_session/slides")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "S1"

def test_get_slides_no_session() -> None:
    """Test retrieving slides for invalid session."""
    with patch("backend.ingestion.router.os.path.exists", return_value=False):
        response = client.get("/ingestion/session/invalid/slides")
        assert response.status_code == 404
