"""
Scan history routes.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.scan import ScanListResponse, ScanSummary
from app.security.jwt_handler import get_current_user
from app.services.scan_service import get_user_scans

router = APIRouter(prefix="/api/scans", tags=["History"])


@router.get("", response_model=ScanListResponse)
def list_scans(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return paginated scan history for the current user."""
    total, scans = get_user_scans(current_user.id, db, skip=skip, limit=limit)
    return ScanListResponse(
        total=total,
        scans=[ScanSummary.model_validate(s) for s in scans],
    )
