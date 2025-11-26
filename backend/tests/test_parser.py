from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from backend.ingestion.parser import extract_from_file

@patch("backend.ingestion.parser.pdfplumber")
def test_extract_from_pdf(mock_pdfplumber: Any) -> None:
    """Test extraction from PDF file."""
    # Mock PDF structure
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page 1 Content"

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]

    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

    slides = extract_from_file("test.pdf")

    assert len(slides) == 1
    assert slides[0].index == 0
    assert slides[0].text == "Page 1 Content"
    assert slides[0].title == "Slide 1" # Default title for PDF

@patch("backend.ingestion.parser.Presentation")
def test_extract_from_pptx(mock_presentation: Any) -> None:
    """Test extraction from PPTX file."""
    # Mock PPTX structure
    mock_slide = MagicMock()
    mock_shape_title = MagicMock()
    mock_shape_title.has_text_frame = True
    mock_shape_title.text = "Slide Title"

    mock_shape_body = MagicMock()
    mock_shape_body.has_text_frame = True
    mock_shape_body.text = "Slide Body"

    mock_shapes = MagicMock()
    mock_shapes.__iter__.return_value = [mock_shape_title, mock_shape_body]
    mock_shapes.title = mock_shape_title

    mock_slide.shapes = mock_shapes

    mock_slide.notes_slide.notes_text_frame.text = "Speaker Notes"

    mock_prs = MagicMock()
    mock_prs.slides = [mock_slide]

    mock_presentation.return_value = mock_prs

    slides = extract_from_file("test.pptx")

    assert len(slides) == 1
    assert slides[0].index == 0
    assert slides[0].title == "Slide Title"
    mock_presentation.assert_called_once_with("test.pptx")
    assert "Slide Body" in slides[0].text
    assert slides[0].notes == "Speaker Notes"

def test_extract_unsupported_format() -> None:
    """Test that unsupported formats raise an error."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_from_file("test.txt")
