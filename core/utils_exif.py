# core/utils_exif.py

from __future__ import annotations

from typing import Optional, Dict, Any
from PIL import Image, ExifTags


def _to_float(value: Any) -> float:
    """
    Convierte un valor EXIF (IFDRational, tuple, int, float) a float.
    """
    try:
        return float(value)
    except Exception:
        pass

    # Tupla (num, den)
    try:
        num, den = value
        return float(num) / float(den)
    except Exception:
        pass

    return float(value)


def _dms_to_dd(dms, ref: str) -> float:
    """
    Convierte coordenadas DMS EXIF a decimal.
    dms suele ser una tupla/lista de 3 valores (grados, minutos, segundos)
    con IFDRational o tuplas (num, den).
    ref es 'N', 'S', 'E' o 'W'.
    """
    if not dms or len(dms) != 3:
        raise ValueError("DMS no tiene 3 componentes")

    degrees = _to_float(dms[0])
    minutes = _to_float(dms[1])
    seconds = _to_float(dms[2])

    value = degrees + (minutes / 60.0) + (seconds / 3600.0)

    if ref in ("S", "W"):
        value = -value

    return value


def extract_gps_from_image(image_file) -> Optional[Dict[str, float]]:
    """
    Extrae lat/lon en decimal a partir de los metadatos EXIF GPS
    de una imagen subida (Django) o de un fichero normal.

    Devuelve:
      {"lat": <float>, "lon": <float>}  si tiene GPS válido
      None                              si no encuentra datos útiles
    """
    # Si viene de Django (ImageFieldFile, InMemoryUploadedFile, etc.)
    f = getattr(image_file, "file", image_file)

    try:
        f.seek(0)
    except Exception:
        pass

    try:
        img = Image.open(f)
    except Exception:
        # No se puede abrir la imagen
        return None

    exif = None
    # Pillow clásico
    try:
        exif = img._getexif()
    except Exception:
        pass

    # Pillow moderno
    if not exif:
        try:
            exif = img.getexif()
        except Exception:
            pass

    if not exif:
        return None

    # Buscar tag GPSInfo
    gps_tag_id = None
    for tag_id, tag_name in ExifTags.TAGS.items():
        if tag_name == "GPSInfo":
            gps_tag_id = tag_id
            break

    if gps_tag_id is None:
        return None

    gps_ifd = exif.get(gps_tag_id)
    if not gps_ifd:
        return None

    # Traducir claves de GPS
    gps_data: Dict[str, Any] = {}
    for key, val in gps_ifd.items():
        name = ExifTags.GPSTAGS.get(key, key)
        gps_data[name] = val

    lat_dms = gps_data.get("GPSLatitude")
    lat_ref = gps_data.get("GPSLatitudeRef")
    lon_dms = gps_data.get("GPSLongitude")
    lon_ref = gps_data.get("GPSLongitudeRef")

    if not (lat_dms and lat_ref and lon_dms and lon_ref):
        return None

    try:
        lat = _dms_to_dd(lat_dms, lat_ref)
        lon = _dms_to_dd(lon_dms, lon_ref)
    except Exception:
        return None

    return {"lat": lat, "lon": lon}
