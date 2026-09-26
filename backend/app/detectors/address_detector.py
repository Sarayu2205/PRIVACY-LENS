"""
Indian address detector.
Detects Indian PIN codes and common address patterns.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_generic

# Indian PIN code: 6-digit code starting with 1-9
_PINCODE_RE = re.compile(
    r"(?i)(?:pin(?:\s*code)?|postal\s+code|zip)[\s:–\-]*([1-9]\d{5})"
)

# Standalone 6-digit number likely to be PIN when surrounded by address context
_STANDALONE_PIN_RE = re.compile(r"(?<!\d)([1-9]\d{5})(?!\d)")

# Address line pattern
_ADDRESS_RE = re.compile(
    r"(?i)(?:address|addr|residence|located at|residing at|flat|house|plot|door)"
    r"[\s:–\-]+(.{10,120}?)(?=\n|\.|$)",
)

_ADDRESS_CONTEXT = re.compile(
    r"(?i)(street|road|nagar|colony|sector|phase|block|district|state|india|mumbai|delhi|bangalore|chennai|hyderabad|pune|kolkata)",
)


class AddressDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        # Detect PIN codes with explicit labels
        for match in _PINCODE_RE.finditer(text):
            span = (match.start(), match.end())
            seen_spans.add(span)
            value = match.group()
            findings.append(RawFinding(
                type="PINCODE",
                value=value,
                masked_value=mask_generic(value, keep_last=2),
                start=match.start(),
                end=match.end(),
                confidence=0.93,
                severity="LOW",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        # Detect full address lines
        for match in _ADDRESS_RE.finditer(text):
            span = (match.start(), match.end())
            if span in seen_spans:
                continue
            seen_spans.add(span)
            value = match.group()
            findings.append(RawFinding(
                type="ADDRESS",
                value=value,
                masked_value="[ADDRESS REDACTED]",
                start=match.start(),
                end=match.end(),
                confidence=0.85,
                severity="MEDIUM",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        return findings
