"""PDF parsing service."""

from io import BytesIO
from typing import BinaryIO

from pypdf import PdfReader


def extract_text_from_pdf(file_obj: BinaryIO) -> str:
    """Extract text from every readable page in a PDF."""
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    data = file_obj.read()
    reader = PdfReader(BytesIO(data))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()
