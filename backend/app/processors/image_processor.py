"""
Image file processor using Tesseract OCR via pytesseract.
Supports PNG, JPG, JPEG.
Preprocessing is applied to improve OCR accuracy.
"""
from typing import Tuple
import io


def _preprocess_image(image):
    """
    Apply basic preprocessing to improve OCR accuracy:
    - Convert to greyscale
    - Increase contrast slightly
    """
    from PIL import ImageEnhance, ImageFilter
    # Convert to greyscale
    image = image.convert("L")
    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)
    # Boost contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    return image


def extract_text_from_image(file_bytes: bytes, lang: str = "eng") -> Tuple[str, float]:
    """
    Extract text from an image using Tesseract OCR.
    Returns (extracted_text, confidence_score).
    
    Requires:
    - pytesseract installed (pip install pytesseract)
    - Tesseract binary installed on the system
    - Pillow installed (pip install Pillow)
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError(
            "pytesseract and/or Pillow not installed. Run: pip install pytesseract Pillow"
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Could not open image: {e}")

    # Preprocess
    processed = _preprocess_image(image)

    # Run OCR
    try:
        # Get detailed output for confidence scoring
        data = pytesseract.image_to_data(
            processed,
            lang=lang,
            output_type=pytesseract.Output.DICT
        )
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR binary not found. "
            "Install from https://github.com/UB-Mannheim/tesseract/wiki (Windows) "
            "or via your package manager."
        )

    # Extract words with confidence
    words = []
    confidences = []
    n_boxes = len(data["level"])

    for i in range(n_boxes):
        conf = int(data["conf"][i])
        text = data["text"][i].strip()
        if conf > 0 and text:
            words.append(text)
            confidences.append(conf)

    extracted_text = pytesseract.image_to_string(processed, lang=lang)

    if not extracted_text.strip():
        raise ValueError(
            "OCR could not extract any text from the image. "
            "Ensure the image is clear and contains readable text."
        )

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return extracted_text, avg_confidence / 100.0
