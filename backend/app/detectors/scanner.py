"""
PrivacyLens Master Scanner.
Runs all detectors on a given text, deduplicates overlapping findings,
and returns a unified list of RawFinding objects.
"""
from typing import List, Dict, Any
from app.detectors.base import RawFinding
from app.detectors.email_detector import EmailDetector
from app.detectors.phone_detector import PhoneDetector
from app.detectors.pan_detector import PANDetector
from app.detectors.aadhaar_detector import AadhaarDetector
from app.detectors.card_detector import CardDetector
from app.detectors.password_detector import PasswordDetector
from app.detectors.api_key_detector import ApiKeyDetector
from app.detectors.jwt_detector import JWTDetector
from app.detectors.private_key_detector import PrivateKeyDetector
from app.detectors.address_detector import AddressDetector
from app.detectors.dob_detector import DOBDetector
from app.detectors.bank_account_detector import BankAccountDetector

# Instantiate all detectors once (shared across requests)
_DETECTORS = [
    EmailDetector(),
    PhoneDetector(),
    PANDetector(),
    AadhaarDetector(),
    CardDetector(),
    PasswordDetector(),
    ApiKeyDetector(),
    JWTDetector(),
    PrivateKeyDetector(),
    AddressDetector(),
    DOBDetector(),
    BankAccountDetector(),
]


def _overlaps(span1: tuple, span2: tuple) -> bool:
    """Return True if two (start, end) spans overlap."""
    return span1[0] < span2[1] and span2[0] < span1[1]


def _deduplicate(findings: List[RawFinding]) -> List[RawFinding]:
    """
    Remove overlapping findings, keeping the one with higher confidence.
    When two findings overlap, the one with higher confidence wins.
    """
    # Sort by confidence descending
    sorted_findings = sorted(findings, key=lambda f: f.confidence, reverse=True)
    accepted: List[RawFinding] = []

    for candidate in sorted_findings:
        candidate_span = (candidate.start, candidate.end)
        if not any(_overlaps(candidate_span, (a.start, a.end)) for a in accepted):
            accepted.append(candidate)

    # Return in document order
    return sorted(accepted, key=lambda f: f.start)


def scan_text(text: str) -> List[RawFinding]:
    """
    Run all detectors on `text` and return deduplicated findings.
    This is the main entry point for the scanner.
    """
    all_findings: List[RawFinding] = []

    for detector in _DETECTORS:
        try:
            results = detector.detect(text)
            all_findings.extend(results)
        except Exception as e:
            # Don't let one detector crash the whole scan
            import logging
            logging.warning(f"Detector {detector.__class__.__name__} failed: {e}")

    return _deduplicate(all_findings)


def get_categories_summary(findings: List[RawFinding]) -> Dict[str, int]:
    """Return a count of findings per category type."""
    summary: Dict[str, int] = {}
    for f in findings:
        summary[f.type] = summary.get(f.type, 0) + 1
    return summary
