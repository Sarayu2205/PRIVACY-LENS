"""
PAN-like pattern detector.
Format: AAAAA0000A (5 uppercase letters, 4 digits, 1 uppercase letter).
This detector uses only pattern-matching on synthetic data.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_generic

# Official PAN structure: LLLLLNNNNL
_PAN_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{5}[0-9]{4}[A-Z])(?![A-Z0-9])")

_PAN_CONTEXT = re.compile(
    r"(pan|permanent\s+account|income\s+tax|it\s+return)",
    re.IGNORECASE
)


class PANDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        for match in _PAN_RE.finditer(text):
            value = match.group()
            window = text[max(0, match.start() - 80):match.end() + 80]
            confidence = 0.92 if _PAN_CONTEXT.search(window) else 0.78

            findings.append(RawFinding(
                type="PAN",
                value=value,
                masked_value=mask_generic(value, keep_last=4),
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                severity="HIGH",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))
        return findings
