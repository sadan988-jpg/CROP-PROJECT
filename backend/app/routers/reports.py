"""Router for PDF claim report generation.

Endpoint:
GET /reports/{claim_id}
    → Calls ``generate_claim_pdf`` and streams the PDF back to the client
      with ``Content-Type: application/pdf`` and a ``Content-Disposition``
      header so the browser downloads it as ``claim_<id>.pdf``.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..reports.pdf_generator import generate_claim_pdf

router = APIRouter()

@router.get("/{claim_id}", response_class=StreamingResponse)
def get_claim_pdf(claim_id: int):
    try:
        pdf_bytes = generate_claim_pdf(claim_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    # Stream the PDF bytes
    def iter_bytes():
        yield pdf_bytes
    headers = {
        "Content-Disposition": f"attachment; filename=claim_{claim_id}.pdf"
    }
    return StreamingResponse(iter_bytes(), media_type="application/pdf", headers=headers)

