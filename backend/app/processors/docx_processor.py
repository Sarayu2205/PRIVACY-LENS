"""
DOCX file processor using python-docx.
Extracts text from paragraphs and tables.
"""
from typing import Tuple
import io


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from a DOCX file's raw bytes.
    Returns (full_text, paragraph_count).
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is not installed. Run: pip install python-docx")

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Could not open DOCX file: {e}")

    parts = []

    # Extract paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            parts.append(text)

    # Extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_texts = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    row_texts.append(cell_text)
            if row_texts:
                parts.append(" | ".join(row_texts))

    if not parts:
        raise ValueError("DOCX file appears to be empty.")

    return "\n".join(parts), len(parts)
