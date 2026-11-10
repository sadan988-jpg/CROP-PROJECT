"""Analytics engine for crop image processing.

The implementation is deliberately lightweight for the initial prototype:
* **Pre‑processing** – Load the uploaded image, resize to 224×224, convert to
  NumPy array.
* **Segmentation** – Use Otsu thresholding on the grayscale version to obtain a
  binary mask that roughly separates vegetation (foreground) from background.
* **Severity calculation** – Compute the percentage of foreground pixels
  relative to the total image area.
* **Disease classification** – A simple placeholder that picks a class at random
  from a known list.  A real model can be swapped in later by replacing the
  `dummy_classifier` function.

The public function `process_image` returns a dictionary with the mask (as a
base‑64 PNG for easy transport), the severity percentage, and the predicted
disease label.
"""

import base64
import io
import random
from typing import Dict

import cv2
import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _pil_to_np(image: Image.Image) -> np.ndarray:
    """Convert a PIL Image to a NumPy array (RGB order)."""
    return np.array(image.convert("RGB"))


def _resize(img_np: np.ndarray, size: int = 224) -> np.ndarray:
    """Resize image to ``size``×``size`` using bilinear interpolation."""
    return cv2.resize(img_np, (size, size), interpolation=cv2.INTER_LINEAR)


def _otsu_mask(gray: np.ndarray) -> np.ndarray:
    """Return a binary mask using Otsu's threshold on a grayscale image.

    The mask has value 255 for foreground (vegetation) and 0 for background.
    """
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask


def _mask_to_base64(mask: np.ndarray) -> str:
    """Encode a mask (uint8) as a base‑64 PNG string."""
    pil_img = Image.fromarray(mask)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def dummy_classifier(_img_np: np.ndarray) -> str:
    """Placeholder classifier – randomly selects a disease class.

    In production you would load a trained Torch / TensorFlow model and run
    inference here.
    """
    classes = [
        "Healthy",
        "Paddy Blast",
        "Sheath Blight",
        "Maize Drought",
        "Submerged Flooding",
    ]
    return random.choice(classes)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def process_image(image_bytes: bytes) -> Dict[str, any]:
    """Run the full analytics pipeline on a raw image.

    Parameters
    ----------
    image_bytes:
        The raw bytes of the uploaded image (e.g. from a multipart/form‑data
        upload).

    Returns
    -------
    dict
        ``{"severity": float, "disease": str, "mask_base64": str}``
    """
    # Load image via PIL
    pil_img = Image.open(io.BytesIO(image_bytes))
    # Resize & convert to NumPy
    img_np = _pil_to_np(pil_img)
    img_np = _resize(img_np, size=224)

    # Segmentation – Otsu on grayscale
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    mask = _otsu_mask(gray)

    # Severity = foreground pixel ratio * 100
    foreground_pixels = np.count_nonzero(mask)
    total_pixels = mask.size
    severity = (foreground_pixels / total_pixels) * 100.0

    # Dummy disease prediction
    disease = dummy_classifier(img_np)

    # Encode mask for transport back to the client
    mask_b64 = _mask_to_base64(mask)

    return {
        "severity": round(severity, 2),
        "disease": disease,
        "mask_base64": mask_b64,
    }

# When this module is imported, the heavy libraries are already loaded, which is
# fine for the prototype.  In a real deployment you may want to lazily load a
# Torch model only once and reuse it across requests.

