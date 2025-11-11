from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from rest_framework import viewsets

from .models import Flight, Photo, Zone
from .serializers import FlightSerializer, PhotoSerializer, ZoneSerializer
from .forms import PhotoUploadForm


# --- API DRF ---

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().order_by('-date', 'id')
    serializer_class = FlightSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-taken_at', 'id')
    serializer_class = PhotoSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer


# --- Vista HTML: subir foto (usa PhotoUploadForm) ---

@require_http_methods(["GET", "POST"])
def upload_photo(request):
    """
    Formulario de subida de fotos.
    - Si la imagen tiene EXIF GPS, el form intentará rellenar lat/lon en clean().
    - Si no, el usuario debe indicar lat/lon manualmente.
    """
    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        # Si no es válido, re-renderizamos con errores
        return render(request, 'upload_photo.html', {'form': form})
    else:
        form = PhotoUploadForm()
        return render(request, 'upload_photo.html', {'form': form})
