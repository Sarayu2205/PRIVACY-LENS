"""Pydantic schemas for Scan and Finding."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class FindingOut(BaseModel):
    id: int
    type: str
    masked_value: Optional[str]
    confidence: float
    location: Optional[str]
    severity: str
    context_snippet: Optional[str]

    model_config = {"from_attributes": True}


class ScanOut(BaseModel):
    id: int
    user_id: int
    file_name: str
    scan_type: str
    risk_score: float
    risk_level: str
    finding_count: int
    categories: Optional[Dict[str, Any]]
    is_masked: bool
    scan_date: datetime
    findings: List[FindingOut] = []

    model_config = {"from_attributes": True}


class ScanSummary(BaseModel):
    id: int
    file_name: str
    scan_type: str
    risk_score: float
    risk_level: str
    finding_count: int
    is_masked: bool
    scan_date: datetime

    model_config = {"from_attributes": True}


class TextScanRequest(BaseModel):
    text: str
    label: Optional[str] = "Pasted Text"


class ScanListResponse(BaseModel):
    total: int
    scans: List[ScanSummary]


class DashboardStats(BaseModel):
    total_scans: int
    total_findings: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    critical_count: int
    recent_scans: List[ScanSummary]
    findings_by_category: Dict[str, int]
    scans_over_time: List[Dict[str, Any]]
