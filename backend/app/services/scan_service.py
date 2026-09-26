"""
PrivacyLens – Scan Service.
Orchestrates: text extraction → detection → NLP enrichment → risk analysis → DB persistence.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.detectors.scanner import scan_text, get_categories_summary
from app.services.nlp_service import extract_named_entities, enrich_findings_with_context
from app.services.risk_analyzer import (
    calculate_risk, build_recommendations, build_risk_summary, get_finding_severity
)
from app.services.masking_service import generate_masked_report_text
from app.models.scan import Scan
from app.models.finding import Finding
from app.detectors.base import RawFinding

logger = logging.getLogger(__name__)


def run_scan(
    text: str,
    file_name: str,
    scan_type: str,
    user_id: int,
    db: Session,
) -> Dict[str, Any]:
    """
    Full scan pipeline:
    1. Run regex detectors
    2. Run NER (NLP)
    3. Deduplicate
    4. Risk analysis
    5. Masking
    6. Persist to DB
    7. Return result dict
    """
    # ── Step 1: Regex detection ────────────────────────────────────────────
    findings: List[RawFinding] = scan_text(text)

    # ── Step 2: NLP named entity extraction ───────────────────────────────
    try:
        nlp_findings = extract_named_entities(text)
        # Merge NLP findings (avoid duplicating positions already covered)
        existing_spans = {(f.start, f.end) for f in findings}
        for nf in nlp_findings:
            if (nf.start, nf.end) not in existing_spans:
                findings.append(nf)
                existing_spans.add((nf.start, nf.end))
    except Exception as e:
        logger.warning(f"NLP enrichment skipped: {e}")

    # ── Step 3: Risk analysis ──────────────────────────────────────────────
    risk_score, risk_level = calculate_risk(findings)
    recommendations = build_recommendations(findings)
    risk_summary = build_risk_summary(risk_score, risk_level, findings)
    categories = get_categories_summary(findings)

    # ── Step 4: Masking ────────────────────────────────────────────────────
    masked_text, _ = generate_masked_report_text(text, findings)

    # ── Step 5: Context enrichment ─────────────────────────────────────────
    enriched = enrich_findings_with_context(text, findings)

    # ── Step 6: Persist scan record ────────────────────────────────────────
    scan = Scan(
        user_id=user_id,
        file_name=file_name,
        scan_type=scan_type,
        risk_score=risk_score,
        risk_level=risk_level,
        finding_count=len(findings),
        categories=categories,
        is_masked=False,
    )
    db.add(scan)
    db.flush()  # Get scan.id without committing

    # Persist findings (never store raw sensitive values)
    for f in findings:
        finding_record = Finding(
            scan_id=scan.id,
            type=f.type,
            masked_value=f.masked_value,
            confidence=f.confidence,
            location=f.location,
            severity=get_finding_severity(f.type),
            context_snippet=f.context_snippet,
        )
        db.add(finding_record)

    db.commit()
    db.refresh(scan)

    # ── Step 7: Build response ─────────────────────────────────────────────
    return {
        "scan_id": scan.id,
        "file_name": file_name,
        "scan_type": scan_type,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "finding_count": len(findings),
        "categories": categories,
        "findings": enriched,
        "masked_text": masked_text,
        "risk_summary": risk_summary,
        "recommendations": recommendations,
        "scan_date": scan.scan_date.isoformat() if scan.scan_date else None,
    }


def get_scan_by_id(scan_id: int, user_id: int, db: Session) -> Optional[Scan]:
    """Fetch a scan owned by the given user."""
    return (
        db.query(Scan)
        .filter(Scan.id == scan_id, Scan.user_id == user_id)
        .first()
    )


def get_user_scans(
    user_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> tuple:
    """Return (total_count, list_of_scans) for a user."""
    query = db.query(Scan).filter(Scan.user_id == user_id).order_by(Scan.scan_date.desc())
    total = query.count()
    scans = query.offset(skip).limit(limit).all()
    return total, scans


def delete_scan(scan_id: int, user_id: int, db: Session) -> bool:
    """Delete a scan and its findings. Returns True if deleted."""
    scan = get_scan_by_id(scan_id, user_id, db)
    if not scan:
        return False
    db.delete(scan)
    db.commit()
    return True
