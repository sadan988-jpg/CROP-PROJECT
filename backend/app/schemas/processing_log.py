"""Pydantic schemas for ProcessingLog model.

Used for returning processing status of a claim.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProcessingLogBase(BaseModel):
    claim_id: int
    timestamp: datetime = None
    status: str
    details: Optional[str] = None

class ProcessingLogCreate(ProcessingLogBase):
    timestamp: datetime = None  # will be set automatically if omitted

class ProcessingLog(ProcessingLogBase):
    id: int

    class Config:
        orm_mode = True

