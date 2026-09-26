"""
Base class for all PrivacyLens detectors.
Every detector returns a list of Finding dicts with a consistent schema.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class RawFinding:
    """Internal finding structure produced by each detector."""
    type: str               # e.g. "EMAIL", "PHONE", "API_KEY"
    value: str              # The actual matched text (used for masking, never stored)
    masked_value: str       # Pre-masked representation
    start: int              # Character offset in full text
    end: int                # Character offset in full text
    confidence: float       # 0.0 – 1.0
    severity: str           # LOW | MEDIUM | HIGH | CRITICAL
    location: str           # Human-readable location, e.g. "Line 4"
    context_snippet: str    # ±40 chars around the match (masked)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "value": self.value,
            "masked_value": self.masked_value,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "severity": self.severity,
            "location": self.location,
            "context_snippet": self.context_snippet,
        }


def build_location(text: str, start: int) -> str:
    """Return 'Line N, Col M' for the given character offset."""
    lines = text[:start].split("\n")
    line_num = len(lines)
    col_num = len(lines[-1]) + 1
    return f"Line {line_num}, Col {col_num}"


def extract_context(text: str, start: int, end: int, window: int = 40) -> str:
    """Return a context snippet with the sensitive value redacted."""
    ctx_start = max(0, start - window)
    ctx_end = min(len(text), end + window)
    snippet = text[ctx_start:ctx_end]
    # Replace the actual value with [REDACTED] in the snippet
    local_start = start - ctx_start
    local_end = end - ctx_start
    redacted = snippet[:local_start] + "[REDACTED]" + snippet[local_end:]
    return redacted.replace("\n", " ").strip()


class BaseDetector:
    """Abstract base – subclasses implement _detect()."""

    def detect(self, text: str) -> List[RawFinding]:
        raise NotImplementedError
