"""ORM model – findings table."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class Finding(Base):
    __tablename__ = "findings"

    id              = Column(Integer, primary_key=True, index=True)
    scan_id         = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    type            = Column(String(50), nullable=False, index=True)
    masked_value    = Column(String(500))
    confidence      = Column(Float, nullable=False, default=0.0)
    location        = Column(String(100))
    severity        = Column(Enum("LOW", "MEDIUM", "HIGH", "CRITICAL"), nullable=False, default="LOW")
    context_snippet = Column(String(500))

    scan = relationship("Scan", back_populates="findings")
