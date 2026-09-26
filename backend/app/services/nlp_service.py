"""
PrivacyLens – NLP/AI Enhancement Service.

Uses spaCy for named entity recognition (NER) to:
1. Detect personal names, organizations, and locations not caught by regex.
2. Provide context analysis — distinguish "Order: 9876543210" from "Phone: 9876543210".
3. Enrich findings with context explanations.

Falls back gracefully if spaCy model is unavailable.
"""
import logging
from typing import List, Dict, Any, Optional
from app.detectors.base import RawFinding, build_location, extract_context

logger = logging.getLogger(__name__)

# spaCy model — loaded once at module level (lazy)
_NLP = None
_NLP_AVAILABLE = False


def _load_nlp():
    """Lazy-load spaCy model. Sets _NLP_AVAILABLE flag."""
    global _NLP, _NLP_AVAILABLE
    if _NLP is not None:
        return _NLP

    try:
        import spacy
        from app.config import settings
        _NLP = spacy.load(settings.SPACY_MODEL)
        _NLP_AVAILABLE = True
        logger.info(f"spaCy model '{settings.SPACY_MODEL}' loaded successfully.")
        return _NLP
    except OSError:
        logger.warning(
            "spaCy model 'en_core_web_sm' not found. "
            "Run: python -m spacy download en_core_web_sm\n"
            "NLP enrichment will be skipped."
        )
        _NLP_AVAILABLE = False
        return None
    except ImportError:
        logger.warning("spaCy not installed. NLP enrichment will be skipped.")
        _NLP_AVAILABLE = False
        return None


def analyze_context(text: str, finding: RawFinding) -> str:
    """
    Analyze the context around a finding to provide a human-readable explanation.
    Uses simple rule-based context matching.
    Returns an explanation string.
    """
    window_start = max(0, finding.start - 80)
    window_end = min(len(text), finding.end + 80)
    context = text[window_start:window_end].lower()

    # Context keywords that indicate genuine personal data usage
    personal_keywords = [
        "my", "your", "his", "her", "their", "contact", "reach", "call",
        "email", "send", "message", "name", "profile", "user", "customer",
        "employee", "patient", "student", "applicant", "account holder"
    ]

    # Context keywords that suggest it might be reference/order numbers
    reference_keywords = [
        "order", "invoice", "reference", "ref", "ticket", "serial",
        "tracking", "item", "product", "catalogue", "code"
    ]

    personal_score = sum(1 for kw in personal_keywords if kw in context)
    reference_score = sum(1 for kw in reference_keywords if kw in context)

    if finding.type == "PHONE":
        if reference_score > personal_score:
            return "Detected as possible phone number, but context suggests it may be a reference/order number."
        elif personal_score > 0:
            return "Phone number detected in personal contact context — likely genuine personal data."
        else:
            return "Phone-like number detected without clear context."

    elif finding.type == "EMAIL":
        return "Email address detected — likely personal or organizational contact information."

    elif finding.type in ("API_KEY", "PASSWORD", "JWT_TOKEN", "PRIVATE_KEY"):
        return "Security credential detected — immediate redaction recommended."

    elif finding.type in ("PAN", "AADHAAR"):
        return "Government-issued identity document number detected — high privacy risk."

    elif finding.type == "CREDIT_CARD":
        return "Payment card number detected — critical financial data exposure."

    elif finding.type == "BANK_ACCOUNT":
        return "Bank account information detected — critical financial data exposure."

    elif finding.type == "DATE_OF_BIRTH":
        return "Date of birth detected — can be used for identity reconstruction."

    else:
        return f"{finding.type.replace('_', ' ').title()} detected."


def extract_named_entities(text: str) -> List[RawFinding]:
    """
    Use spaCy NER to detect PERSON names, ORG names, and LOCATION entities
    that are not caught by regex patterns.
    Returns additional RawFinding objects.
    Falls back to empty list if spaCy unavailable.
    """
    nlp = _load_nlp()
    if nlp is None:
        return []

    findings: List[RawFinding] = []

    try:
        # Limit text length to prevent memory issues on large documents
        doc = nlp(text[:50000])

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                from app.utils.masking import mask_generic
                findings.append(RawFinding(
                    type="PERSON_NAME",
                    value=ent.text,
                    masked_value=mask_generic(ent.text, keep_last=0),
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.82,
                    severity="MEDIUM",
                    location=build_location(text, ent.start_char),
                    context_snippet=extract_context(text, ent.start_char, ent.end_char),
                ))

    except Exception as e:
        logger.warning(f"NER extraction failed: {e}")

    return findings


def enrich_findings_with_context(text: str, findings: List[RawFinding]) -> List[Dict[str, Any]]:
    """
    Enrich each finding with an NLP-derived context explanation.
    Returns findings as dicts with added 'context_explanation' key.
    """
    enriched = []
    for f in findings:
        d = f.to_dict()
        d["context_explanation"] = analyze_context(text, f)
        enriched.append(d)
    return enriched


def is_nlp_available() -> bool:
    """Return True if spaCy model is loaded and available."""
    _load_nlp()
    return _NLP_AVAILABLE
