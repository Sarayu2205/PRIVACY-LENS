"""
JWT / access token detector.
Identifies the classic three-part base64url.base64url.base64url structure.
"""
import re
import json
import base64
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_full

# JWT: header.payload.signature (each part is base64url, min 10 chars each)
_JWT_RE = re.compile(
    r"(?<![A-Za-z0-9\-_])"
    r"(ey[A-Za-z0-9\-_]{10,}\.ey[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,})"
    r"(?![A-Za-z0-9\-_])"
)


def _decode_jwt_header(token: str) -> dict:
    """Try to decode the JWT header for extra confidence."""
    try:
        header_b64 = token.split(".")[0]
        # Add padding
        padding = 4 - len(header_b64) % 4
        header_b64 += "=" * (padding % 4)
        decoded = base64.urlsafe_b64decode(header_b64)
        return json.loads(decoded)
    except Exception:
        return {}


class JWTDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        for match in _JWT_RE.finditer(text):
            token = match.group(1)
            header = _decode_jwt_header(token)

            # Boost confidence if header contains "alg" and "typ"
            if header.get("alg") and header.get("typ") == "JWT":
                confidence = 0.99
            else:
                confidence = 0.90

            # Show only header portion to user, mask the rest
            parts = token.split(".")
            masked = f"{parts[0]}.{'*' * 20}.{'*' * 20}"

            findings.append(RawFinding(
                type="JWT_TOKEN",
                value=token,
                masked_value=masked,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                severity="CRITICAL",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))
        return findings
