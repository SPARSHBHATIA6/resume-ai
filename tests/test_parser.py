from io import BytesIO

from reportlab.pdfgen import canvas

from services.pdf_parser import extract_text_from_pdf


def test_pdf_extraction():
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(50, 750, "Aarav Mehta Python Developer")
    c.save()
    buffer.seek(0)
    text = extract_text_from_pdf(buffer)
    assert "Aarav Mehta" in text
