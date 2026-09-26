"""
Scan routes: text scan, file scan, get scan, delete scan, mask scan.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.finding import Finding
from app.schemas.scan import TextScanRequest, ScanOut, ScanListResponse, ScanSummary
from app.security.jwt_handler import get_current_user
from app.processors.file_handler import process_uploaded_file
from app.services.scan_service import run_scan, get_scan_by_id, get_user_scans, delete_scan

router = APIRouter(prefix="/api/scan", tags=["Scanning"])


@router.post("/text")
def scan_text_endpoint(
    payload: TextScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan plain text for sensitive data."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    if len(payload.text) > 500_000:
        raise HTTPException(status_code=413, detail="Text too large. Maximum 500,000 characters.")

    result = run_scan(
        text=payload.text,
        file_name=payload.label or "Pasted Text",
        scan_type="text",
        user_id=current_user.id,
        db=db,
    )
    return result


@router.post("/file")
async def scan_file_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and scan a file (TXT, PDF, DOCX, PNG, JPG)."""
    extracted_text, safe_name = await process_uploaded_file(file)

    result = run_scan(
        text=extracted_text,
        file_name=safe_name,
        scan_type="file",
        user_id=current_user.id,
        db=db,
    )
    return result


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific scan with all findings."""
    scan = (
        db.query(Scan)
        .filter(Scan.id == scan_id, Scan.user_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@router.delete("/{scan_id}", status_code=204)
def delete_scan_endpoint(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a scan and all its findings."""
    deleted = delete_scan(scan_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found.")


@router.post("/{scan_id}/mask")
def mark_scan_masked(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a scan as masked (user confirmed they downloaded the sanitized version)."""
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    scan.is_masked = True
    db.commit()
    return {"message": "Scan marked as masked.", "scan_id": scan_id}
