"""ORM model – reports table."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id         = Column(Integer, primary_key=True, index=True)
    scan_id    = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True)
    file_path  = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scan = relationship("Scan", back_populates="report")
