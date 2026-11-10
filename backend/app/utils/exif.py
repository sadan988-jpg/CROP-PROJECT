"""Utility functions for extracting GPS information from image EXIF data.

We use the `piexif` library because it works purely with bytes and does not
require Pillow to read the file.  The helper `_dms_to_decimal` converts the
rational DMS (degrees/minutes/seconds) format used in EXIF into a float.

The public function ``extract_gps`` returns a dict with ``latitude`` and
``longitude`` keys (or ``None`` if the data is missing).
"""

import piexif
from typing import Optional, Dict


def _dms_to_decimal(dms, ref) -> Optional[float]:
    """Convert EXIF DMS tuple to decimal degrees.

    ``dms`` is a tuple of three rational numbers (num, den). ``ref`` is a
    character like ``N``, ``S``, ``E`` or ``W`` that determines the sign.
    """
    try:
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1]
        seconds = dms[2][0] / dms[2][1]
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        if ref in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return None


def extract_gps(image_bytes: bytes) -> Dict[str, Optional[float]]:
    """Extract GPS latitude & longitude from an image's EXIF block.

    Parameters
    ----------
    image_bytes:
        Raw image data (as received from an upload).

    Returns
    -------
    dict
        ``{"latitude": float|None, "longitude": float|None}``
    """
    try:
        exif_dict = piexif.load(image_bytes)
        gps_ifd = exif_dict.get("GPS", {})
        if not gps_ifd:
            return {"latitude": None, "longitude": None}

        lat_ref = gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef, b"").decode()
        lat = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
        lon_ref = gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef, b"").decode()
        lon = gps_ifd.get(piexif.GPSIFD.GPSLongitude)

        latitude = _dms_to_decimal(lat, lat_ref) if lat and lat_ref else None
        longitude = _dms_to_decimal(lon, lon_ref) if lon and lon_ref else None
        return {"latitude": latitude, "longitude": longitude}
    except Exception:
        # Any parsing error results in missing GPS data
        return {"latitude": None, "longitude": None}

