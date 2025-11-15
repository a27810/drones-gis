from rest_framework import serializers
from .models import Flight, Photo, Zone


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['id', 'name', 'drone_model', 'date', 'path_geojson']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        # flight será el ID del vuelo (o null)
        fields = ['id', 'flight', 'image', 'lat', 'lon', 'taken_at', 'notes']


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'zone_type', 'geometry']
