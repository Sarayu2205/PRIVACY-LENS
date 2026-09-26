"""
Date of Birth detector.
Detects DOB patterns in multiple common Indian/international formats.
Only flags as DOB when the surrounding context suggests it.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_generic

# Date patterns: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, DD Month YYYY
_DATE_PATTERNS = [
    re.compile(r"(?<!\d)((?:0?[1-9]|[12]\d|3[01])[/\-](0?[1-9]|1[0-2])[/\-](?:19|20)\d{2})(?!\d)"),
    re.compile(r"(?<!\d)((?:19|20)\d{2}[/\-](0?[1-9]|1[0-2])[/\-](?:0?[1-9]|[12]\d|3[01]))(?!\d)"),
    re.compile(
        r"(?<!\d)((?:0?[1-9]|[12]\d|3[01])\s+"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+(?:19|20)\d{2})(?!\d)",
        re.IGNORECASE
    ),
]

_DOB_CONTEXT = re.compile(
    r"(?i)(date\s+of\s+birth|dob|born\s+on|birth\s+date|d\.o\.b)",
)


class DOBDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        for pattern in _DATE_PATTERNS:
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if span in seen_spans:
                    continue

                window = text[max(0, match.start() - 80):match.end() + 80]
                has_dob_context = bool(_DOB_CONTEXT.search(window))

                # Only flag as DOB if context suggests it; otherwise skip
                if not has_dob_context:
                    continue

                seen_spans.add(span)
                value = match.group()

                findings.append(RawFinding(
                    type="DATE_OF_BIRTH",
                    value=value,
                    masked_value="[DOB REDACTED]",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90,
                    severity="HIGH",
                    location=build_location(text, match.start()),
                    context_snippet=extract_context(text, match.start(), match.end()),
                ))
        return findings
