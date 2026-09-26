"""
Plain-text file processor.
Reads .txt files safely with encoding detection fallback.
"""
import chardet
from typing import Tuple


def extract_text_from_txt(file_bytes: bytes) -> Tuple[str, str]:
    """
    Extract text from a TXT file's raw bytes.
    Returns (extracted_text, encoding_used).
    Tries UTF-8 first, then chardet detection, then latin-1 as last resort.
    """
    # Try UTF-8
    try:
        return file_bytes.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        pass

    # Try chardet detection
    detection = chardet.detect(file_bytes)
    encoding = detection.get("encoding") or "latin-1"
    try:
        return file_bytes.decode(encoding), encoding
    except (UnicodeDecodeError, LookupError):
        pass

    # Final fallback
    return file_bytes.decode("latin-1", errors="replace"), "latin-1"
