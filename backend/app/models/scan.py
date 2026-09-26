"""ORM model – scans table."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name     = Column(String(255), nullable=False)
    scan_type     = Column(Enum("file", "text"), nullable=False, default="file")
    risk_score    = Column(Float, nullable=False, default=0.0)
    risk_level    = Column(Enum("LOW", "MEDIUM", "HIGH", "CRITICAL"), nullable=False, default="LOW")
    finding_count = Column(Integer, nullable=False, default=0)
    categories    = Column(JSON)
    is_masked     = Column(Boolean, default=False)
    scan_date     = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user     = relationship("User", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    report   = relationship("Report", back_populates="scan", uselist=False, cascade="all, delete-orphan")
