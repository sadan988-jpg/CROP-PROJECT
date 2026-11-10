from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # e.g., "started", "completed", "failed"
    details = Column(Text, nullable=True)    # optional free‑form debug info

    claim = relationship("Claim", back_populates="logs")

