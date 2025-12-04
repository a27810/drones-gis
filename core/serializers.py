from rest_framework import serializers
from .models import Photo, Flight, Zone


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            'id',
            'flight',
            'image',
            'lat',
            'lon',
            'taken_at',
            'notes',
        ]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            'id',
            'name',
            'drone_model',
            'date',
            'path_geojson',
        ]


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = [
            'id',
            'name',
            'zone_type',
            'geometry',
        ]
