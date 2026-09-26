"""
Private key / certificate detector.
Detects PEM-encoded private keys, certificates, and similar sensitive crypto material.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_full

_PEM_PATTERNS = [
    ("PRIVATE_KEY",     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", re.MULTILINE)),
    ("CERTIFICATE",     re.compile(r"-----BEGIN CERTIFICATE-----[\s\S]+?-----END CERTIFICATE-----", re.MULTILINE)),
    ("PGP_PRIVATE_KEY", re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----[\s\S]+?-----END PGP PRIVATE KEY BLOCK-----", re.MULTILINE)),
    ("SSH_PRIVATE_KEY", re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+?-----END OPENSSH PRIVATE KEY-----", re.MULTILINE)),
    ("PRIVATE_KEY",     re.compile(r"-----BEGIN PRIVATE KEY-----")),   # Partial / single line
]


class PrivateKeyDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []
        seen_spans: set = set()

        for key_type, pattern in _PEM_PATTERNS:
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                # Skip if already captured by a more specific pattern
                if any(s <= match.start() and match.end() <= e for (s, e) in seen_spans):
                    continue
                seen_spans.add(span)

                full_text = match.group()
                header_line = full_text.split("\n")[0]

                findings.append(RawFinding(
                    type=key_type,
                    value=full_text,
                    masked_value=f"{header_line}\n[KEY CONTENT REDACTED]\n-----END ...",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.99,
                    severity="CRITICAL",
                    location=build_location(text, match.start()),
                    context_snippet=f"[{key_type} detected — content redacted]",
                ))
        return findings
