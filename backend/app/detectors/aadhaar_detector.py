"""
Aadhaar-like 12-digit pattern detector.
Supports formats: XXXX XXXX XXXX  and  XXXXXXXXXXXX
All detection is purely pattern-based on synthetic test data only.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_aadhaar

# Spaced: 1234 5678 9012
_AADHAAR_SPACED = re.compile(r"(?<!\d)([2-9]\d{3}\s\d{4}\s\d{4})(?!\d)")
# Continuous: 123456789012 (must start with 2-9, no surrounding digits)
_AADHAAR_CONT   = re.compile(r"(?<!\d)([2-9]\d{11})(?!\d)")

_AADHAAR_CONTEXT = re.compile(
    r"(aadhaar|aadhar|uid\b|unique\s+id|uidai)",
    re.IGNORECASE
)


class AadhaarDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        for pattern in [_AADHAAR_SPACED, _AADHAAR_CONT]:
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if span in seen_spans:
                    continue
                seen_spans.add(span)

                value = match.group()
                window = text[max(0, match.start() - 80):match.end() + 80]
                confidence = 0.93 if _AADHAAR_CONTEXT.search(window) else 0.72

                findings.append(RawFinding(
                    type="AADHAAR",
                    value=value,
                    masked_value=mask_aadhaar(value),
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    severity="HIGH",
                    location=build_location(text, match.start()),
                    context_snippet=extract_context(text, match.start(), match.end()),
                ))
        return findings
