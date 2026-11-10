"""Pydantic schemas for Claim model.

These schemas are used in request/response bodies for the API.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ClaimBase(BaseModel):
    farmer_id: int
    plot_area_acres: float = Field(..., gt=0)
    sum_insured_per_acre: float = Field(..., gt=0)
    severity_percent: float = Field(..., ge=0, le=100)
    estimated_payout: float = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # optional GPS, image_path etc. can be added later

class ClaimCreate(ClaimBase):
    pass

class Claim(ClaimBase):
    id: int

    class Config:
        orm_mode = True

