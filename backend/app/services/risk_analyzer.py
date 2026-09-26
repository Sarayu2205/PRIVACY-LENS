"""
PrivacyLens – Risk Analysis Service.

Transparent, documented scoring formula:
─────────────────────────────────────────────────────────────────────
Each finding contributes:
    base_score = TYPE_WEIGHT[type] * confidence

Aggregation:
    raw_score = sum of all finding base_scores, capped at 100

Severity thresholds:
    0  – 24  → LOW
    25 – 49  → MEDIUM
    50 – 74  → HIGH
    75 – 100 → CRITICAL

Type weights (max contribution per finding):
    CRITICAL types (weight 20): PASSWORD, API_KEY, JWT_TOKEN,
                                PRIVATE_KEY, CREDIT_CARD, BANK_ACCOUNT
    HIGH types     (weight 15): PAN, AADHAAR, DATE_OF_BIRTH
    MEDIUM types   (weight 10): PHONE, ADDRESS, IFSC_CODE
    LOW types      (weight  5): EMAIL, PINCODE
─────────────────────────────────────────────────────────────────────
"""
from typing import List, Dict, Tuple
from app.detectors.base import RawFinding

# Weight per finding type (contribution to risk score per finding)
TYPE_WEIGHTS: Dict[str, float] = {
    # Critical severity
    "PASSWORD":     20.0,
    "API_KEY":      20.0,
    "JWT_TOKEN":    20.0,
    "PRIVATE_KEY":  20.0,
    "CREDIT_CARD":  20.0,
    "BANK_ACCOUNT": 20.0,
    # High severity
    "PAN":          15.0,
    "AADHAAR":      15.0,
    "DATE_OF_BIRTH":15.0,
    # Medium severity
    "PHONE":        10.0,
    "ADDRESS":      10.0,
    "IFSC_CODE":     8.0,
    # Low severity
    "EMAIL":         5.0,
    "PINCODE":       3.0,
}

# Severity thresholds
_THRESHOLDS = [
    (75.0, "CRITICAL"),
    (50.0, "HIGH"),
    (25.0, "MEDIUM"),
    (0.0,  "LOW"),
]

# Map type → severity
TYPE_SEVERITY: Dict[str, str] = {
    "PASSWORD":     "CRITICAL",
    "API_KEY":      "CRITICAL",
    "JWT_TOKEN":    "CRITICAL",
    "PRIVATE_KEY":  "CRITICAL",
    "CREDIT_CARD":  "CRITICAL",
    "BANK_ACCOUNT": "CRITICAL",
    "PAN":          "HIGH",
    "AADHAAR":      "HIGH",
    "DATE_OF_BIRTH":"HIGH",
    "PHONE":        "MEDIUM",
    "ADDRESS":      "MEDIUM",
    "IFSC_CODE":    "MEDIUM",
    "EMAIL":        "LOW",
    "PINCODE":      "LOW",
}


def get_finding_severity(finding_type: str) -> str:
    return TYPE_SEVERITY.get(finding_type, "LOW")


def calculate_risk(findings: List[RawFinding]) -> Tuple[float, str]:
    """
    Calculate risk score and level for a list of findings.
    Returns (score: float 0-100, level: str).
    """
    if not findings:
        return 0.0, "LOW"

    raw_score = 0.0
    for f in findings:
        weight = TYPE_WEIGHTS.get(f.type, 5.0)
        raw_score += weight * f.confidence

    # Cap at 100
    score = min(100.0, raw_score)

    # Determine level
    level = "LOW"
    for threshold, lvl in _THRESHOLDS:
        if score >= threshold:
            level = lvl
            break

    return round(score, 2), level


def build_recommendations(findings: List[RawFinding]) -> List[str]:
    """
    Generate actionable recommendations based on detected finding types.
    """
    found_types = {f.type for f in findings}
    recs = []

    if "PASSWORD" in found_types:
        recs.append("🔑 Remove hardcoded passwords immediately and rotate any exposed credentials.")
    if "API_KEY" in found_types:
        recs.append("🔐 Revoke and regenerate all exposed API keys. Use environment variables to store secrets.")
    if "JWT_TOKEN" in found_types:
        recs.append("🪙 Invalidate any exposed JWT tokens and check your token expiry policy.")
    if "PRIVATE_KEY" in found_types:
        recs.append("🗝️  Immediately revoke the exposed private key and generate a new key pair.")
    if "CREDIT_CARD" in found_types:
        recs.append("💳 Remove credit card numbers from all documents. Never store card data in plain text.")
    if "BANK_ACCOUNT" in found_types:
        recs.append("🏦 Redact bank account numbers before sharing documents.")
    if "AADHAAR" in found_types:
        recs.append("🪪 Mask Aadhaar numbers — share only the last 4 digits as per UIDAI guidelines.")
    if "PAN" in found_types:
        recs.append("📋 Redact PAN numbers before sharing documents or uploading to third-party systems.")
    if "DATE_OF_BIRTH" in found_types:
        recs.append("📅 Remove dates of birth from shared documents to prevent identity reconstruction.")
    if "EMAIL" in found_types:
        recs.append("📧 Consider masking email addresses in publicly shared documents.")
    if "PHONE" in found_types:
        recs.append("📞 Remove phone numbers from documents before sharing to avoid unwanted contact.")
    if "ADDRESS" in found_types:
        recs.append("🏠 Redact physical addresses before sharing documents externally.")

    if not recs:
        recs.append("✅ No sensitive information detected. Document appears safe to share.")

    return recs


def build_risk_summary(score: float, level: str, findings: List[RawFinding]) -> str:
    """
    Build a human-readable risk summary paragraph.
    """
    count = len(findings)
    critical_count = sum(1 for f in findings if get_finding_severity(f.type) == "CRITICAL")

    if level == "CRITICAL":
        return (
            f"CRITICAL RISK — This document contains {count} sensitive finding(s), "
            f"including {critical_count} critical exposure(s) such as passwords, API keys, "
            f"or financial credentials. Do NOT share this document without redaction."
        )
    elif level == "HIGH":
        return (
            f"HIGH RISK — {count} finding(s) detected including government-issued IDs or "
            f"financial information. Redact sensitive data before sharing."
        )
    elif level == "MEDIUM":
        return (
            f"MEDIUM RISK — {count} finding(s) detected including personal contact information. "
            f"Review findings and mask before sharing externally."
        )
    else:
        return (
            f"LOW RISK — {count} finding(s) detected. Minor personal information found. "
            f"Review before sharing."
        )
