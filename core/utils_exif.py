from __future__ import annotations
from typing import Optional, Tuple
from PIL import Image, ExifTags


def _to_degrees(value) -> Optional[float]:
    """
    Convierte un valor EXIF de tipo GPS (tupla de racionales)
    a grados decimales.
    Ejemplo: ((40,1), (25,1), (12,1)) -> 40 + 25/60 + 12/3600
    """
    try:
        # value suele ser una tupla de 3 tuplas: (deg, min, sec)
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None


def extract_gps_from_image(file_obj) -> Optional[Tuple[float, float]]:
    """
    Extrae (lat, lon) en grados decimales desde los metadatos EXIF de una imagen.

    - Tiene en cuenta GPSLatitudeRef (N/S)
    - Tiene en cuenta GPSLongitudeRef (E/W)
    - Devuelve None si no hay información válida.
    """
    try:
        # Asegurarnos de leer desde el principio del fichero
        if hasattr(file_obj, "open"):
            # Para FieldFile (ImageField en Django)
            file_obj.open()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        img = Image.open(file_obj)

        exif_raw = img._getexif()
        if not exif_raw:
            return None

        # Mapear IDs numéricos a nombres de etiqueta
        exif = {
            ExifTags.TAGS.get(tag, tag): value
            for tag, value in exif_raw.items()
        }

        gps_info = exif.get("GPSInfo")
        if not gps_info:
            return None

        # Decodificar sub-etiquetas GPS
        gps_data = {
            ExifTags.GPSTAGS.get(tag, tag): value
            for tag, value in gps_info.items()
        }

        lat = lon = None

        lat_vals = gps_data.get("GPSLatitude")
        lat_ref = gps_data.get("GPSLatitudeRef")
        lon_vals = gps_data.get("GPSLongitude")
        lon_ref = gps_data.get("GPSLongitudeRef")

        # --- Latitud ---
        if lat_vals and lat_ref:
            lat_deg = _to_degrees(lat_vals)
            if lat_deg is not None:
                # Sur (S) -> negativa
                if str(lat_ref).upper().startswith("S"):
                    lat_deg = -lat_deg
                lat = lat_deg

        # --- Longitud ---
        if lon_vals and lon_ref:
            lon_deg = _to_degrees(lon_vals)
            if lon_deg is not None:
                # Oeste (W) -> negativa
                if str(lon_ref).upper().startswith("W"):
                    lon_deg = -lon_deg
                lon = lon_deg

        if lat is not None and lon is not None:
            return lat, lon

        return None

    except Exception:
        # Si algo peta leyendo EXIF, simplemente devolvemos None
        return None
