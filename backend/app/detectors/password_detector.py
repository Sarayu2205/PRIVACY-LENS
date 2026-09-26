"""
Password / credential detector.
Detects assignment patterns like: password=MySecret123
Also detects common credential keys in config files and code.
"""
import re
from typing import List
from app.detectors.base import BaseDetector, RawFinding, build_location, extract_context
from app.utils.masking import mask_full

# Match: key = "value"  or  key: value  or  key=value
_CRED_RE = re.compile(
    r"(?i)"
    r"(?P<key>"
    r"password|passwd|pass|pwd|secret|credentials?|db_pass(?:word)?|"
    r"auth_pass|login_pass|admin_pass|root_pass"
    r")"
    r"\s*[=:\"'\s]+\s*"
    r"(?P<val>[^\s\"',;}{>\n]{4,80})",
)

# Detect HTTP Basic Auth header
_BASIC_AUTH_RE = re.compile(
    r"(?i)Authorization\s*:\s*Basic\s+([A-Za-z0-9+/=]{8,})"
)


class PasswordDetector(BaseDetector):
    def detect(self, text: str) -> List[RawFinding]:
        findings: List[RawFinding] = []

        for match in _CRED_RE.finditer(text):
            full = match.group()
            val = match.group("val")
            # Skip obvious placeholders
            if val.lower() in {"your_password", "xxxx", "****", "changeme", "placeholder", "example", "<password>"}:
                continue

            findings.append(RawFinding(
                type="PASSWORD",
                value=full,
                masked_value=f"{match.group('key')}={'*' * len(val)}",
                start=match.start(),
                end=match.end(),
                confidence=0.93,
                severity="CRITICAL",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        for match in _BASIC_AUTH_RE.finditer(text):
            full = match.group()
            findings.append(RawFinding(
                type="PASSWORD",
                value=full,
                masked_value="Authorization: Basic [REDACTED]",
                start=match.start(),
                end=match.end(),
                confidence=0.98,
                severity="CRITICAL",
                location=build_location(text, match.start()),
                context_snippet=extract_context(text, match.start(), match.end()),
            ))

        return findings
