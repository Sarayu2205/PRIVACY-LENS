"""
Dashboard statistics route.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.finding import Finding
from app.schemas.scan import DashboardStats, ScanSummary
from app.security.jwt_handler import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated statistics for the dashboard."""
    uid = current_user.id

    # Total scans
    total_scans = db.query(func.count(Scan.id)).filter(Scan.user_id == uid).scalar() or 0

    # Total findings
    total_findings = (
        db.query(func.sum(Scan.finding_count))
        .filter(Scan.user_id == uid)
        .scalar() or 0
    )

    # Risk-level counts
    risk_counts = (
        db.query(Scan.risk_level, func.count(Scan.id))
        .filter(Scan.user_id == uid)
        .group_by(Scan.risk_level)
        .all()
    )
    risk_map = {r: c for r, c in risk_counts}

    # Findings by category — from findings table joined to user scans
    category_rows = (
        db.query(Finding.type, func.count(Finding.id))
        .join(Scan, Finding.scan_id == Scan.id)
        .filter(Scan.user_id == uid)
        .group_by(Finding.type)
        .all()
    )
    findings_by_category = {row[0]: row[1] for row in category_rows}

    # Recent scans (last 5)
    recent_scans_orm = (
        db.query(Scan)
        .filter(Scan.user_id == uid)
        .order_by(Scan.scan_date.desc())
        .limit(5)
        .all()
    )
    recent_scans = [ScanSummary.model_validate(s) for s in recent_scans_orm]

    # Scans over time — last 30 days, grouped by day
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_scans = (
        db.query(
            func.date(Scan.scan_date).label("day"),
            func.count(Scan.id).label("count"),
        )
        .filter(Scan.user_id == uid, Scan.scan_date >= thirty_days_ago)
        .group_by(func.date(Scan.scan_date))
        .order_by(func.date(Scan.scan_date))
        .all()
    )
    scans_over_time = [{"date": str(row.day), "count": row.count} for row in daily_scans]

    return DashboardStats(
        total_scans=total_scans,
        total_findings=int(total_findings),
        high_risk_count=risk_map.get("HIGH", 0),
        medium_risk_count=risk_map.get("MEDIUM", 0),
        low_risk_count=risk_map.get("LOW", 0),
        critical_count=risk_map.get("CRITICAL", 0),
        recent_scans=recent_scans,
        findings_by_category=findings_by_category,
        scans_over_time=scans_over_time,
    )
