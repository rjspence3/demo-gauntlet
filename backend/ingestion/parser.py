import os
from typing import List
import pdfplumber
from pptx import Presentation
from backend.models.core import Slide

def extract_from_file(file_path: str) -> List[Slide]:
    """
    Extracts slides from a PDF or PPTX file.

    Args:
        file_path: Path to the file.

    Returns:
        List of Slide objects.

    Raises:
        ValueError: If the file format is not supported.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    if ext == ".pptx":
        return _extract_from_pptx(file_path)

    raise ValueError(f"Unsupported file format: {ext}")

def _extract_from_pdf(file_path: str) -> List[Slide]:
    slides = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # PDF doesn't have explicit titles, so we use a generic one or first line
            title = f"Slide {i + 1}"
            slides.append(Slide(index=i, title=title, text=text))
    return slides

def _extract_from_pptx(file_path: str) -> List[Slide]:
    slides = []
    prs = Presentation(file_path)

    for i, slide in enumerate(prs.slides):
        title = ""
        text_parts = []

        # Try to get title
        if slide.shapes.title and slide.shapes.title.has_text_frame:
            title = slide.shapes.title.text
        else:
            title = f"Slide {i + 1}"

        # Get all text
        for shape in slide.shapes:
            if shape.has_text_frame:
                text_parts.append(shape.text)

        text = "\n".join(text_parts)

        # Get notes
        notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text

        slides.append(Slide(index=i, title=title, text=text, notes=notes))

    return slides
