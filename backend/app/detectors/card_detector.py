"""
Credit / Debit card number detector.
Uses regex patterns for Visa, Mastercard, Amex, RuPay, etc.
Applies the Luhn algorithm to reduce false positives.
IMPORTANT: Never store or log real card numbers.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_card

# Common card patterns (spaces or dashes allowed between groups)
_CARD_RE = re.compile(
    r"(?<!\d)"
    r"((?:4\d{3}|5[1-5]\d{2}|2[2-7]\d{2}|3[47]\d{2}|6(?:011|5\d{2})|(?:508[5-9]|6069[8-9]|607[0-9]|608[0-4]))"  # BIN
    r"(?:[\s\-]?\d{4}){2,3}"  # remaining groups
    r"(?:[\s\-]?\d{2,4})?)"
    r"(?!\d)",
    re.VERBOSE,
)


def _luhn_check(number: str) -> bool:
    """Return True if number passes the Luhn algorithm."""
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13:
        return False
    total = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


class CardDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        for match in _CARD_RE.finditer(text):
            value = match.group()
            digits = re.sub(r"\D", "", value)

            # Must be 13-19 digits and pass Luhn check
            if len(digits) < 13 or len(digits) > 19:
                continue
            if not _luhn_check(digits):
                continue

            findings.append(RawFinding(
                type="CREDIT_CARD",
                value=value,
                masked_value=mask_card(value),
                start=match.start(),
                end=match.end(),
                confidence=0.97,   # Luhn passing makes this high-confidence
                severity="CRITICAL",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))
        return findings
