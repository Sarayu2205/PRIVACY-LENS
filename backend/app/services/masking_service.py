"""
PrivacyLens – Masking Service.
Applies all detector findings to the original text and produces
a sanitized (masked) version of the document.
"""
from typing import List, Tuple
from app.detectors.base import RawFinding
from app.utils.masking import apply_mask_to_text


def mask_text(original_text: str, findings: List[RawFinding]) -> str:
    """
    Apply masking to the original text using finding spans.
    Returns the sanitized text.
    """
    if not findings:
        return original_text

    finding_dicts = [f.to_dict() for f in findings]
    return apply_mask_to_text(original_text, finding_dicts)


def mask_single_value(finding_type: str, value: str) -> str:
    """
    Mask a single value by its finding type.
    Used for display in reports without relying on span positions.
    """
    from app.utils.masking import (
        mask_email, mask_generic, mask_full,
        mask_aadhaar, mask_card
    )

    type_upper = finding_type.upper()

    if type_upper == "EMAIL":
        return mask_email(value)
    elif type_upper in ("CREDIT_CARD",):
        return mask_card(value)
    elif type_upper == "AADHAAR":
        return mask_aadhaar(value)
    elif type_upper in ("PASSWORD", "API_KEY", "JWT_TOKEN", "PRIVATE_KEY"):
        return mask_full(value)
    elif type_upper in ("PAN",):
        return mask_generic(value, keep_last=4)
    elif type_upper in ("PHONE", "BANK_ACCOUNT"):
        return mask_generic(value, keep_last=4)
    else:
        return mask_generic(value, keep_last=3)


def generate_masked_report_text(original_text: str, findings: List[RawFinding]) -> Tuple[str, int]:
    """
    Generate sanitized text and return (masked_text, count_of_replacements).
    """
    masked = mask_text(original_text, findings)
    return masked, len(findings)
