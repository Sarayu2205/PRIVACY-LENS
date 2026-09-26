"""
PDF file processor using PyMuPDF (fitz).
Extracts text from all pages, preserving paragraph structure.
"""
from typing import Tuple


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from a PDF's raw bytes using PyMuPDF.
    Returns (full_text, page_count).
    Raises ValueError if the file cannot be parsed.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is not installed. Run: pip install pymupdf")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Could not open PDF: {e}")

    pages_text = []
    page_count = len(doc)  # Get page count BEFORE closing

    for page_num in range(page_count):
        page = doc[page_num]
        # Extract text with layout preservation
        text = page.get_text("text")
        if text.strip():
            pages_text.append(f"[Page {page_num + 1}]\n{text}")

    doc.close()  # Close AFTER we're done reading

    if not pages_text:
        raise ValueError(
            "PDF appears to be empty or image-only. "
            "Try scanning as an image (PNG/JPG) instead."
        )

    return "\n\n".join(pages_text), page_count
