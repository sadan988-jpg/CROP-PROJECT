"""FastAPI router for claim‑related operations.

Endpoints:
* **GET /claims/** – list all claims (optional `farmer_id` query param).
* **GET /claims/{claim_id}** – retrieve a single claim.
* **DELETE /claims/{claim_id}** – delete a claim (admin‑style operation).

All responses use the Pydantic `Claim` schema defined in
`app.schemas.claim`.  The router is registered in `app.main` under the
`/claims` prefix.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.claim import Claim as ClaimModel
from ..schemas.claim import Claim as ClaimSchema

router = APIRouter()

@router.get("/", response_model=list[ClaimSchema])
def list_claims(
    farmer_id: int | None = Query(None, description="Filter by farmer ID"),
    db: Session = Depends(get_db),
):
    query = db.query(ClaimModel)
    if farmer_id is not None:
        query = query.filter(ClaimModel.farmer_id == farmer_id)
    return query.all()

@router.get("/{claim_id}", response_model=ClaimSchema)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(ClaimModel).filter(ClaimModel.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@router.delete("/{claim_id}", response_model=dict)
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(ClaimModel).filter(ClaimModel.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    db.delete(claim)
    db.commit()
    return {"detail": f"Claim {claim_id} deleted"}

