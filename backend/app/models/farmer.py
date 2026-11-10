from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    # Additional farmer metadata can be added later

    # Relationship to claims
    claims = relationship("Claim", back_populates="farmer")

