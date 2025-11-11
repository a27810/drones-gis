# core/utils_exif.py
from typing import Optional, Tuple, Any
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

def _dms_to_dd(dms, ref) -> float:
    """Convierte DMS (rationals) a decimal y aplica signo por Ref."""
    def _to_float(x: Any) -> float:
        # x puede ser un tuple (num, den) o ya float
        if isinstance(x, (tuple, list)) and len(x) == 2:
            num, den = x
            return float(num) / float(den) if den else 0.0
        return float(x)
    degrees = _to_float(dms[0])
    minutes = _to_float(dms[1])
    seconds = _to_float(dms[2])
    dd = degrees + minutes / 60.0 + seconds / 3600.0
    ref = ref.decode() if isinstance(ref, (bytes, bytearray)) else ref
    if ref in ('S', 'W'):
        dd = -dd
    return dd

def _pillow_exif(img: Image.Image) -> Optional[Tuple[float, float]]:
    """Intenta extraer GPS vía Pillow."""
    try:
        exif = img._getexif() or {}
    except Exception:
        exif = {}
    if not exif:
        return None
    exif_map = {TAGS.get(k, k): v for k, v in exif.items()}
    gps_raw = exif_map.get('GPSInfo')
    if not gps_raw:
        return None
    gps = {GPSTAGS.get(k, k): v for k, v in gps_raw.items()}
    lat, lat_ref = gps.get('GPSLatitude'), gps.get('GPSLatitudeRef')
    lon, lon_ref = gps.get('GPSLongitude'), gps.get('GPSLongitudeRef')
    if not (lat and lon and lat_ref and lon_ref):
        return None
    return _dms_to_dd(lat, lat_ref), _dms_to_dd(lon, lon_ref)

def _piexif_from_bytes(data: bytes) -> Optional[Tuple[float, float]]:
    """Intenta extraer GPS leyendo EXIF con piexif desde los bytes completos."""
    try:
        exif_dict = piexif.load(data)
    except Exception:
        return None
    gps = exif_dict.get('GPS') or {}
    lat = gps.get(piexif.GPSIFD.GPSLatitude)
    lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef)
    lon = gps.get(piexif.GPSIFD.GPSLongitude)
    lon_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef)
    if not (lat and lon and lat_ref and lon_ref):
        return None
    return _dms_to_dd(lat, lat_ref), _dms_to_dd(lon, lon_ref)

def extract_gps_from_image(file_obj) -> Optional[Tuple[float, float]]:
    """
    Estrategia:
      1) Pillow._getexif()
      2) piexif.load() desde bytes del archivo
    Devuelve (lat, lon) o None.
    """
    try:
        # 1) Pillow
        try:
            file_obj.seek(0)
        except Exception:
            pass
        img = Image.open(file_obj)
        coords = _pillow_exif(img)
        if coords:
            return coords

        # 2) piexif desde bytes
        try:
            file_obj.seek(0)
            data = file_obj.read()
        except Exception:
            data = None
        if data:
            coords = _piexif_from_bytes(data)
            if coords:
                return coords
    except Exception:
        pass
    return None
