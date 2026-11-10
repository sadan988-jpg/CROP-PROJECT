from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    plot_area_acres = Column(Float, nullable=False)
    sum_insured_per_acre = Column(Float, nullable=False)
    severity_percent = Column(Float, nullable=False)
    estimated_payout = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    # Additional fields such as image path, etc.

    farmer = relationship("Farmer", back_populates="claims")
    logs = relationship("ProcessingLog", back_populates="claim")

