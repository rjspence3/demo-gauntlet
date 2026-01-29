"""
Tests for parser.
"""
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

    mock_pdf.metadata = {"Author": "Test Author"}
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

    slides, metadata = extract_from_file("test.pdf")

    assert len(slides) == 1
    assert slides[0].index == 0
    assert slides[0].text == "Page 1 Content"
    assert slides[0].title == "Slide 1" # Default title for PDF
    assert metadata == {"Author": "Test Author"}

@patch("backend.ingestion.parser.Presentation")
def test_extract_from_pptx(mock_presentation: Any) -> None:
    """Test extraction from PPTX file."""
    # Mock PPTX structure
    mock_slide = MagicMock()
    # Mock Title Shape
    mock_shape_title = MagicMock()
    mock_shape_title.has_text_frame = True
    mock_shape_title.has_table = False
    mock_shape_title.shape_type = 1
    
    mock_title_run = MagicMock()
    mock_title_run.text = "Slide Title"
    mock_title_p = MagicMock()
    mock_title_p.runs = [mock_title_run]
    mock_shape_title.text_frame.paragraphs = [mock_title_p]
    mock_shape_title.text = "Slide Title"
    
    # Mock Body Shape
    mock_shape_body = MagicMock()
    mock_shape_body.has_text_frame = True
    mock_shape_body.has_table = False
    mock_shape_body.shape_type = 1
    
    mock_body_run = MagicMock()
    mock_body_run.text = "Slide Body"
    mock_body_p = MagicMock()
    mock_body_p.runs = [mock_body_run]
    mock_shape_body.text_frame.paragraphs = [mock_body_p]

    mock_shapes = MagicMock()
    mock_shapes.__iter__.return_value = [mock_shape_title, mock_shape_body]
    mock_shapes.title = mock_shape_title

    mock_slide.shapes = mock_shapes

    mock_slide.notes_slide.notes_text_frame.text = "Speaker Notes"

    mock_prs = MagicMock()
    mock_prs.slides = [mock_slide]
    mock_prs.core_properties.author = "PPTX Author"
    mock_prs.core_properties.created = "2023-01-01"
    mock_prs.core_properties.modified = "2023-01-02"
    mock_prs.core_properties.title = "Deck Title"

    mock_presentation.return_value = mock_prs

    slides, metadata = extract_from_file("test.pptx")

    assert len(slides) == 1
    assert slides[0].index == 0
    assert slides[0].title == "Slide Title"
    mock_presentation.assert_called_once_with("test.pptx")
    assert "Slide Body" in slides[0].text
    assert slides[0].notes == "Speaker Notes"
    assert metadata["author"] == "PPTX Author"

def test_extract_unsupported_format() -> None:
    """Test that unsupported formats raise an error."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_from_file("test.txt")
