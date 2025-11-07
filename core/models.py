from django.db import models

class Flight(models.Model):
    name = models.CharField(max_length=120)
    drone_model = models.CharField(max_length=120, blank=True)
    date = models.DateField(null=True, blank=True)
    # MVP: almacenamos la ruta como GeoJSON (LineString)
    path_geojson = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

class Photo(models.Model):
    flight = models.ForeignKey(Flight, null=True, blank=True, on_delete=models.SET_NULL, related_name='photos')
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
