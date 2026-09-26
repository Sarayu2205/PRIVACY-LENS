"""
Email address detector.
Detects standard RFC-5321-like email addresses.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_email

# RFC-5321 simplified pattern – covers all common formats
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE
)


class EmailDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        for match in _EMAIL_RE.finditer(text):
            value = match.group()
            findings.append(RawFinding(
                type="EMAIL",
                value=value,
                masked_value=mask_email(value),
                start=match.start(),
                end=match.end(),
                confidence=0.97,
                severity="MEDIUM",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))
        return findings
