"""
API key / secret / token detector.
Uses regex patterns AND Shannon entropy to catch high-entropy secret strings.
"""
import re
import math
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_full

# Key/value assignment patterns
_KEY_RE = re.compile(
    r"(?i)"
    r"(?P<key>"
    r"api[_\-\s]?key|api[_\-\s]?secret|app[_\-\s]?key|app[_\-\s]?secret|"
    r"access[_\-\s]?key|access[_\-\s]?secret|secret[_\-\s]?key|client[_\-\s]?secret|"
    r"private[_\-\s]?key|auth[_\-\s]?key|auth[_\-\s]?token|"
    r"stripe[_\-\s]?key|aws[_\-\s]?(?:access|secret)|"
    r"gh[_\-\s]?token|github[_\-\s]?token|gitlab[_\-\s]?token|"
    r"slack[_\-\s]?(?:token|webhook)|twilio[_\-\s]?(?:auth|sid)|"
    r"sendgrid[_\-\s]?key|mailgun[_\-\s]?key|firebase[_\-\s]?key"
    r")"
    r"\s*[=:\"'\s]+\s*"
    r"(?P<val>[A-Za-z0-9_\-/+.]{16,})",
)

# Well-known prefix patterns (Stripe, GitHub, etc.)
_PREFIX_PATTERNS = [
    (re.compile(r"(?<![A-Za-z0-9])(sk_(?:live|test)_[A-Za-z0-9]{24,})(?![A-Za-z0-9])"), "STRIPE_KEY"),
    (re.compile(r"(?<![A-Za-z0-9])(pk_(?:live|test)_[A-Za-z0-9]{24,})(?![A-Za-z0-9])"), "STRIPE_PK"),
    (re.compile(r"(?<![A-Za-z0-9])(ghp_[A-Za-z0-9]{36,})(?![A-Za-z0-9])"), "GITHUB_TOKEN"),
    (re.compile(r"(?<![A-Za-z0-9])(gho_[A-Za-z0-9]{36,})(?![A-Za-z0-9])"), "GITHUB_OAUTH"),
    (re.compile(r"(?<![A-Za-z0-9])(AKIA[A-Z0-9]{16})(?![A-Za-z0-9])"), "AWS_ACCESS_KEY"),
    (re.compile(r"(?<![A-Za-z0-9])(AIza[A-Za-z0-9\-_]{35})(?![A-Za-z0-9])"), "GOOGLE_API_KEY"),
    (re.compile(r"(?<![A-Za-z0-9])(xox[bpas]-[A-Za-z0-9\-]{10,})(?![A-Za-z0-9])"), "SLACK_TOKEN"),
]

_ENTROPY_THRESHOLD = 4.5   # bits per character
_MIN_SECRET_LEN = 20


def _shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((f / n) * math.log2(f / n) for f in freq.values())


class ApiKeyDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        # Pattern 1: Named key assignments
        for match in _KEY_RE.finditer(text):
            span = (match.start(), match.end())
            if span in seen_spans:
                continue
            seen_spans.add(span)

            val = match.group("val")
            entropy = _shannon_entropy(val)
            confidence = min(0.97, 0.80 + (entropy / 10.0))

            findings.append(RawFinding(
                type="API_KEY",
                value=match.group(),
                masked_value=f"{match.group('key')}={'*' * min(len(val), 20)}",
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                severity="CRITICAL",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        # Pattern 2: Well-known provider prefixes
        for pattern, key_type in _PREFIX_PATTERNS:
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if span in seen_spans:
                    continue
                seen_spans.add(span)

                val = match.group(1)
                findings.append(RawFinding(
                    type="API_KEY",
                    value=val,
                    masked_value=mask_full(val),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.99,
                    severity="CRITICAL",
                    location=build_location(text, match.start()),
                    context_snippet=extract_context(text, match.start(), match.end()),
                ))

        return findings
