"""
PrivacyLens – Masking utility functions.
Used by detectors and the masking service.
"""
import re


def mask_email(email: str) -> str:
    """student@gmail.com → s******@gmail.com"""
    if "@" not in email:
        return "*" * len(email)
    local, domain = email.rsplit("@", 1)
    if len(local) <= 1:
        return f"*@{domain}"
    return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"


def mask_generic(value: str, keep_last: int = 4) -> str:
    """Replace all but the last N characters with asterisks."""
    value = value.strip()
    if len(value) <= keep_last:
        return "*" * len(value)
    return "*" * (len(value) - keep_last) + value[-keep_last:]


def mask_full(value: str) -> str:
    """Replace entire value with asterisks."""
    return "*" * min(len(value), 32)


def mask_aadhaar(value: str) -> str:
    """1234 5678 9012 → **** **** 9012"""
    digits = re.sub(r"\D", "", value)
    if len(digits) == 12:
        return f"**** **** {digits[-4:]}"
    return mask_generic(value, keep_last=4)


def mask_card(value: str) -> str:
    """4111 1111 1111 1111 → **** **** **** 1111"""
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 12:
        return f"**** **** **** {digits[-4:]}"
    return mask_generic(value, keep_last=4)


def apply_mask_to_text(text: str, findings: list) -> str:
    """
    Apply masking to the original text using finding spans.
    Processes findings in reverse order to preserve offsets.
    Returns the sanitized text.
    """
    # Sort by start position descending to preserve offsets
    sorted_findings = sorted(findings, key=lambda f: f["start"], reverse=True)
    result = list(text)

    for finding in sorted_findings:
        start = finding["start"]
        end = finding["end"]
        masked = finding["masked_value"]
        result[start:end] = list(masked)

    return "".join(result)
