import os
import base64
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.farmer import Farmer
from ..models.claim import Claim
from ..models.processing_log import ProcessingLog
from ..schemas.claim import ClaimCreate, Claim
from ..analytics.engine import process_image
from ..utils.exif import extract_gps

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=Claim)
async def analyze_and_create_claim(
    image: UploadFile = File(...),
    farmer_id: int = Form(...),
    plot_area_acres: float = Form(...),
    sum_insured_per_acre: float = Form(...),
    db: Session = Depends(get_db),
):
    # Verify farmer exists
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # Read image bytes
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    # Run analytics pipeline
    results = process_image(image_bytes)
    severity = results["severity"]
    disease = results["disease"]
    mask_b64 = results["mask_base64"]

    # Extract GPS from EXIF (if present)
    gps_data = extract_gps(image_bytes)
    latitude = gps_data["latitude"]
    longitude = gps_data["longitude"]

    # Estimate payout using PMFBY formula (severity must be >=15%)
    eligible = severity >= 15.0
    estimated_payout = (
        plot_area_acres * sum_insured_per_acre * (severity / 100.0) if eligible else 0.0
    )

    # Persist claim record, including optional GPS coordinates
    claim_data = ClaimCreate(
        farmer_id=farmer_id,
        plot_area_acres=plot_area_acres,
        sum_insured_per_acre=sum_insured_per_acre,
        severity_percent=severity,
        estimated_payout=estimated_payout,
        created_at=datetime.utcnow(),
        latitude=latitude,
        longitude=longitude,
    )
    claim = Claim(**claim_data.dict())
    db.add(claim)
    db.commit()
    db.refresh(claim)

    # Save original image and mask for later download/reporting
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    img_path = os.path.join(UPLOAD_DIR, f"claim_{claim.id}_{timestamp}.png")
    mask_path = os.path.join(UPLOAD_DIR, f"claim_{claim.id}_{timestamp}_mask.png")
    with open(img_path, "wb") as f:
        f.write(image_bytes)
    # Decode the mask from base64 and write it
    mask_bytes = base64.b64decode(mask_b64)
    with open(mask_path, "wb") as f:
        f.write(mask_bytes)

    # Create processing log entry
    log = ProcessingLog(
        claim_id=claim.id,
        timestamp=datetime.utcnow(),
        status="completed",
        details=f"Severity={severity:.2f}%, disease={disease}, payout={'eligible' if eligible else 'ineligible'}",
    )
    db.add(log)
    db.commit()

    return claim
