"""
PrivacyLens – Unified file handler.
Routes incoming uploaded files to the appropriate processor
and returns normalized extracted text.
"""
import os
import uuid
import tempfile
from typing import Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.processors.txt_processor import extract_text_from_txt
from app.processors.pdf_processor import extract_text_from_pdf
from app.processors.docx_processor import extract_text_from_docx
from app.processors.image_processor import extract_text_from_image

# Max file size in bytes
_MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024

# Allowed MIME types mapped to extension
_ALLOWED_MIME = {
    "text/plain": "txt",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}

_ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "png", "jpg", "jpeg"}


def _safe_extension(filename: str) -> str:
    """Return the lowercase extension without the dot."""
    _, ext = os.path.splitext(filename)
    return ext.lstrip(".").lower()


async def process_uploaded_file(upload: UploadFile) -> Tuple[str, str]:
    """
    Validate, read, and extract text from an uploaded file.
    Returns (extracted_text, safe_filename).
    Raises HTTPException on any failure.
    """
    # Validate extension
    ext = _safe_extension(upload.filename or "")
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. "
                   f"Allowed: {', '.join(_ALLOWED_EXTENSIONS)}"
        )

    # Read bytes
    file_bytes = await upload.read()

    # Validate size
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {settings.MAX_FILE_SIZE_MB} MB."
        )

    # Generate a safe filename (no path traversal)
    safe_name = f"{uuid.uuid4().hex[:8]}_{_sanitize_filename(upload.filename or 'upload')}"

    # Route to appropriate processor
    try:
        if ext == "txt":
            text, _ = extract_text_from_txt(file_bytes)
        elif ext == "pdf":
            text, _ = extract_text_from_pdf(file_bytes)
        elif ext == "docx":
            text, _ = extract_text_from_docx(file_bytes)
        elif ext in ("png", "jpg", "jpeg"):
            text, _ = extract_text_from_image(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Server configuration error: {e}")

    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from the file.")

    return text, safe_name


def _sanitize_filename(filename: str) -> str:
    """Remove path components and dangerous characters from a filename."""
    # Take only the basename
    name = os.path.basename(filename)
    # Replace anything that's not alphanumeric, dot, dash, or underscore
    import re
    name = re.sub(r"[^\w.\-]", "_", name)
    # Limit length
    return name[:128]
