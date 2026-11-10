"""PDF report generator for a claim.

Given a claim ID, it loads the claim record, the original image and the mask
saved in ``backend/uploads/`` and creates a simple PDF using ReportLab.  The PDF
contains:
* Claim metadata (ID, farmer name, severity, payout, GPS if available)
* The uploaded image
* The segmentation mask overlay (shown as a separate image)

The function returns the PDF as a ``bytes`` object so the FastAPI endpoint can
stream it back to the client.
"""

import os
import io
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

from ..database import SessionLocal
from ..models.claim import Claim as ClaimModel
from ..models.farmer import Farmer as FarmerModel

# Directory where analytics router stores images & masks
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))

def _load_image(path: str) -> Image.Image:
    """Open an image file and ensure it is RGB for ReportLab."""
    return Image.open(path).convert("RGB")

def _draw_image(c: canvas.Canvas, img: Image.Image, x: int, y: int, max_width: int, max_height: int) -> int:
    """Draw ``img`` onto the canvas, fitting inside the max dimensions.

    Returns the drawn height (in points) so the caller can adjust the cursor.
    """
    w, h = img.size
    ratio = min(max_width / w, max_height / h, 1)
    w, h = int(w * ratio), int(h * ratio)
    c.drawImage(ImageReader(img), x, y - h, width=w, height=h)
    return h

def generate_claim_pdf(claim_id: int) -> bytes:
    """Generate a PDF for ``claim_id``.

    Raises
    ------
    ValueError
        If the claim does not exist or the image files cannot be located.
    """
    db = SessionLocal()
    try:
        claim: ClaimModel = db.query(ClaimModel).filter(ClaimModel.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        farmer: Optional[FarmerModel] = db.query(FarmerModel).filter(FarmerModel.id == claim.farmer_id).first()
    finally:
        db.close()

    # Locate the image and mask files saved by the analytics router
    base_pattern = f"claim_{claim_id}_"
    image_path = None
    mask_path = None
    if os.path.isdir(UPLOAD_DIR):
        for name in os.listdir(UPLOAD_DIR):
            if name.startswith(base_pattern) and name.endswith('.png'):
                if '_mask' in name:
                    mask_path = os.path.join(UPLOAD_DIR, name)
                else:
                    image_path = os.path.join(UPLOAD_DIR, name)
    if not image_path:
        raise ValueError(f"Original image for claim {claim_id} not found")
    if not mask_path:
        raise ValueError(f"Mask image for claim {claim_id} not found")

    img = _load_image(image_path)
    mask_img = _load_image(mask_path)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4
    margin = 40
    y = page_h - margin

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, f"PMFBY Claim Report – ID #{claim.id}")
    y -= 30

    # Claim details
    c.setFont("Helvetica", 12)
    details = [
        f"Farmer: {farmer.name if farmer else 'N/A'}",
        f"Plot area (acres): {claim.plot_area_acres}",
        f"Sum insured per acre (₹): {claim.sum_insured_per_acre}",
        f"Severity (%): {claim.severity_percent:.2f}",
        f"Estimated payout (₹): {claim.estimated_payout:.2f}",
        f"Created at: {claim.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"GPS: {claim.latitude:.6f}, {claim.longitude:.6f}" if claim.latitude and claim.longitude else "GPS: not available",
    ]
    for line in details:
        c.drawString(margin, y, line)
        y -= 18
    y -= 10

    # Images – allocate half the remaining height to each
    max_img_w = page_w - 2 * margin
    max_img_h = (y - margin) / 2 - 20

    # Original image
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Uploaded Image:")
    y -= 5
    h_drawn = _draw_image(c, img, margin, y, max_img_w, max_img_h)
    y -= h_drawn + 20

    # Mask image
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Segmentation Mask:")
    y -= 5
    _draw_image(c, mask_img, margin, y, max_img_w, max_img_h)

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

