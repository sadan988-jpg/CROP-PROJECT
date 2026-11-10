"""Pydantic schemas for Farmer model.

These schemas are used in request/response bodies for the API.
"""

from pydantic import BaseModel
from typing import Optional, List

class FarmerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None

class FarmerCreate(FarmerBase):
    pass

class Farmer(FarmerBase):
    id: int
    # List of claim IDs could be added later
    class Config:
        orm_mode = True

