#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Genera zonas UAS DEMO por toda España y las añade al fichero
static/geojson/enaire_uas_zones_example.geojson

- Mantiene las features que ya existen en el fichero.
- Añade 200 zonas nuevas (polígonos pequeños).
"""

import json
from pathlib import Path
import itertools

BASE_FILE = Path("static/geojson/enaire_uas_zones_example.geojson")


def main():
    if not BASE_FILE.exists():
        raise SystemExit(f"No se encuentra el fichero {BASE_FILE}")

    data = json.loads(BASE_FILE.read_text(encoding="utf-8"))
    features = data.get("features", [])

    print(f"✔ Zonas existentes en el fichero: {len(features)}")

    # ------------------------------------------------------------------
    # Definimos la "rejilla" sobre España
    #   Aproximadamente:
    #   - Longitudes: de -9.5 a 3.5
    #   - Latitudes:  de 36.0 a 43.9
    #   Usamos un paso moderado para no abarrotarlo demasiado.
    # ------------------------------------------------------------------
    lon_min, lon_max = -9.5, 3.5
    lat_min, lat_max = 36.0, 43.9

    # Paso aproximado (en grados)
    lon_step = 0.7
    lat_step = 0.6

    # Tamaño de cada polígono (cuadradito)
    dlon = 0.20
    dlat = 0.18

    classes = [
        "Zona de control CTR",
        "Zona prohibida",
        "Zona restringida",
        "Zona militar restringida",
        "Zona militar prohibida",
        "Zona urbana sensible",
        "Espacio natural protegido",
        "Infraestructura crítica",
    ]

    types = [
        "Aeropuerto",
        "Base militar",
        "Zona urbana sensible",
        "Zona histórica",
        "Campo de maniobras",
        "Zona industrial crítica",
        "Parque nacional",
        "Reserva natural",
        "Puerto comercial",
        "Instalación logística",
    ]

    new_features = []
    counter = 1

    # Generamos combinaciones de lat/lon
    lats = [lat_min + i * lat_step for i in range(int((lat_max - lat_min) / lat_step) + 1)]
    lons = [lon_min + j * lon_step for j in range(int((lon_max - lon_min) / lon_step) + 1)]

    for lat, lon in itertools.product(lats, lons):
        if counter > 20:
            break

        # Ajustamos límites si se pasan
        lon1 = max(lon, lon_min)
        lon2 = min(lon + dlon, lon_max)
        lat1 = max(lat, lat_min)
        lat2 = min(lat + dlat, lat_max)

        # Pequeño filtro para que quede más o menos dentro de la Península
        # (evitamos demasiadas celdas en pleno mar abierto)
        if lon2 < -9.0 or lon1 > 3.0:
            continue
        if lat2 < 36.0 or lat1 > 43.8:
            continue

        cls = classes[(counter - 1) % len(classes)]
        typ = types[(counter - 1) % len(types)]

        feature = {
            "type": "Feature",
            "properties": {
                "name": f"Zona UAS DEMO #{counter}",
                "class": cls,
                "type": typ,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon1, lat1],
                    [lon2, lat1],
                    [lon2, lat2],
                    [lon1, lat2],
                    [lon1, lat1],
                ]],
            },
        }

        new_features.append(feature)
        counter += 1

    print(f"✔ Zonas nuevas generadas: {len(new_features)}")

    features.extend(new_features)
    data["features"] = features

    BASE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✔ Total de zonas en el fichero tras la generación: {len(features)}")
    print(f"✔ Fichero actualizado: {BASE_FILE}")


if __name__ == "__main__":
    main()
