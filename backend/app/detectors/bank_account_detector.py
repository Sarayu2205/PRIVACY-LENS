"""
Bank account number detector.
Detects Indian bank account patterns (9–18 digits) when surrounded by banking context.
Also detects IFSC codes.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_generic

# Indian bank account: 9-18 digits
_ACCOUNT_RE = re.compile(r"(?<!\d)(\d{9,18})(?!\d)")

# IFSC code: 4 uppercase letters + 0 + 6 alphanumeric
_IFSC_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{4}0[A-Z0-9]{6})(?![A-Z0-9])")

_BANK_CONTEXT = re.compile(
    r"(?i)(account\s+(?:no|number|num)|a/c\s+(?:no|number)|bank\s+account|"
    r"savings\s+account|current\s+account|ifsc|micr|account\s+holder)",
)


class BankAccountDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        # Detect account numbers (only with banking context)
        for match in _ACCOUNT_RE.finditer(text):
            window = text[max(0, match.start() - 100):match.end() + 100]
            if not _BANK_CONTEXT.search(window):
                continue

            span = (match.start(), match.end())
            if span in seen_spans:
                continue
            seen_spans.add(span)

            value = match.group()
            findings.append(RawFinding(
                type="BANK_ACCOUNT",
                value=value,
                masked_value=mask_generic(value, keep_last=4),
                start=match.start(),
                end=match.end(),
                confidence=0.88,
                severity="CRITICAL",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        # Detect IFSC codes
        for match in _IFSC_RE.finditer(text):
            span = (match.start(), match.end())
            if span in seen_spans:
                continue
            seen_spans.add(span)

            value = match.group()
            findings.append(RawFinding(
                type="IFSC_CODE",
                value=value,
                masked_value=mask_generic(value, keep_last=4),
                start=match.start(),
                end=match.end(),
                confidence=0.87,
                severity="MEDIUM",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        return findings
