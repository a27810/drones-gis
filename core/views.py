from rest_framework import viewsets
from .models import Flight, Photo, Zone
from .serializers import FlightSerializer, PhotoSerializer, ZoneSerializer

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().order_by('-date', 'id')
    serializer_class = FlightSerializer

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-taken_at', 'id')
    serializer_class = PhotoSerializer

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
