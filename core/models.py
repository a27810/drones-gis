from django.db import models
import math
import json


class Flight(models.Model):
    name = models.CharField(max_length=120)
    drone_model = models.CharField(max_length=120, blank=True)
    date = models.DateField(null=True, blank=True)
    # MVP: almacenamos la ruta como GeoJSON (LineString)
    path_geojson = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    # ---------- Helpers internos para trabajar con la ruta ----------

    def _extract_line_coordinates(self):
        """
        Devuelve una lista de puntos (lat, lon) a partir de path_geojson.

        Acepta:
          - {"type": "LineString", "coordinates": [[lon, lat], ...]}
          - {"type": "Feature", "geometry": {"type": "LineString", ...}}
        """
        gj = self.path_geojson
        if not gj:
            return []

        # Si se ha guardado como texto, intentamos parsear
        if isinstance(gj, str):
            try:
                gj = json.loads(gj)
            except Exception:
                return []

        if not isinstance(gj, dict):
            return []

        # Sacar la LineString
        if gj.get("type") == "LineString":
            coords = gj.get("coordinates") or []
        elif gj.get("type") == "Feature":
            geom = gj.get("geometry") or {}
            if geom.get("type") == "LineString":
                coords = geom.get("coordinates") or []
            else:
                coords = []
        else:
            coords = []

        points = []
        for c in coords:
            # Cada coord debe ser [lon, lat]
            if not isinstance(c, (list, tuple)) or len(c) < 2:
                continue
            try:
                lon = float(c[0])
                lat = float(c[1])
                points.append((lat, lon))
            except (TypeError, ValueError):
                continue
        return points

    @staticmethod
    def _haversine_km(p1, p2):
        """
        Distancia en km entre dos puntos (lat, lon) usando fórmula de Haversine.
        """
        lat1, lon1 = p1
        lat2, lon2 = p2

        R = 6371.0088  # radio medio de la Tierra en km

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    # ---------- Propiedad de distancia para la plantilla ----------

    @property
    def distance_km(self) -> float:
        """
        Distancia total estimada de la ruta en kilómetros.
        Si no hay ruta o solo hay un punto, devuelve 0.0.
        """
        pts = self._extract_line_coordinates()
        if len(pts) < 2:
            return 0.0

        total = 0.0
        for i in range(1, len(pts)):
            total += self._haversine_km(pts[i - 1], pts[i])
        return total


class Photo(models.Model):
    flight = models.ForeignKey(
        Flight,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='photos'
    )
    image = models.ImageField(upload_to='photos/')
    lat = models.FloatField()
    lon = models.FloatField()
    taken_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'Photo #{self.id}'


class Zone(models.Model):
    name = models.CharField(max_length=120)
    zone_type = models.CharField(max_length=80)  # Prohibida/Restringida/Permitida…
    geometry = models.JSONField()                # GeoJSON Feature/FeatureCollection

    def __str__(self):
        return self.name
