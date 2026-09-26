"""
Indian phone number detector.
Supports: 10-digit mobile, +91 prefix, 0-prefix STD, and spaced formats.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_generic

# Patterns ordered from most-specific to least-specific to reduce false positives
_PHONE_PATTERNS = [
    # +91-XXXXXXXXXX  or  +91 XXXXXXXXXX
    re.compile(r"(?<!\d)(\+91[\s\-]?[6-9]\d{9})(?!\d)"),
    # 0XXXXXXXXXX (11 digits starting with 0)
    re.compile(r"(?<!\d)(0[6-9]\d{9})(?!\d)"),
    # 10-digit mobile starting with 6-9
    re.compile(r"(?<!\d)([6-9]\d{9})(?!\d)"),
    # Spaced formats: XXXXX XXXXX
    re.compile(r"(?<!\d)([6-9]\d{4}[\s\-]\d{5})(?!\d)"),
]

# Minimum surrounding context words that make a phone number more likely
_PHONE_CONTEXT = re.compile(
    r"(phone|mobile|cell|contact|call|whatsapp|ph|mob|no\.?|number)",
    re.IGNORECASE
)


def _score_confidence(text: str, start: int, end: int) -> float:
    """Boost confidence if phone-related keyword is nearby."""
    window = text[max(0, start - 60):end + 60]
    if _PHONE_CONTEXT.search(window):
        return 0.95
    return 0.80


class PhoneDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        for pattern in _PHONE_PATTERNS:
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if span in seen_spans:
                    continue
                seen_spans.add(span)

                value = match.group().strip()
                digits_only = re.sub(r"\D", "", value)

                # Skip sequences that look like order/reference numbers (embedded in longer strings)
                before = text[max(0, match.start() - 1):match.start()]
                after = text[match.end():match.end() + 1]
                if before.isdigit() or after.isdigit():
                    continue

                confidence = _score_confidence(text, match.start(), match.end())

                findings.append(RawFinding(
                    type="PHONE",
                    value=value,
                    masked_value=mask_generic(value, keep_last=4),
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    severity="MEDIUM",
                    location=build_location(text, match.start()),
                    context_snippet=extract_context(text, match.start(), match.end()),
                ))
        return findings
