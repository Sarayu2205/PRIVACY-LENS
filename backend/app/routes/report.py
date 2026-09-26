"""
Report generation and download routes.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.finding import Finding
from app.models.report import Report
from app.security.jwt_handler import get_current_user
from app.services.report_service import generate_pdf_report

router = APIRouter(prefix="/api/report", tags=["Reports"])


@router.get("/{scan_id}/generate")
def generate_report(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate (or regenerate) a PDF security report for a scan."""
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()

    try:
        filepath = generate_pdf_report(scan, findings, db)
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    # Save or update report record
    existing = db.query(Report).filter(Report.scan_id == scan_id).first()
    if existing:
        existing.file_path = filepath
        db.commit()
        report = existing
    else:
        report = Report(scan_id=scan_id, file_path=filepath)
        db.add(report)
        db.commit()
        db.refresh(report)

    return {
        "report_id": report.id,
        "scan_id": scan_id,
        "file_path": os.path.basename(filepath),
        "message": "Report generated successfully.",
    }


@router.get("/{scan_id}/download")
def download_report(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the PDF report for a scan."""
    # Verify ownership
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    report = db.query(Report).filter(Report.scan_id == scan_id).first()
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No report found. Call /generate first."
        )

    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk.")

    return FileResponse(
        path=report.file_path,
        media_type="application/pdf",
        filename=os.path.basename(report.file_path),
    )
