from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from rest_framework import viewsets

from .models import Flight, Photo, Zone
from .serializers import FlightSerializer, PhotoSerializer, ZoneSerializer
from .forms import PhotoUploadForm, FlightForm


# -----------------------
# API REST (DRF)
# -----------------------

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().order_by('-date', 'id')
    serializer_class = FlightSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-taken_at', '-id')
    serializer_class = PhotoSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer


# -----------------------
# Vistas HTML
# -----------------------

def home(request):
    """Pantalla de bienvenida."""
    return render(request, 'welcome.html')


def map_view(request):
    """Visor de mapa (Leaflet)."""
    return render(request, 'map.html')


@require_http_methods(["GET", "POST"])
def upload_photo(request):
    """
    Formulario de subida de fotos.
    Usa PhotoUploadForm, que ya se encarga de EXIF / validación.
    """
    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # después de subir, volvemos al inicio o al mapa
            return redirect('home')
    else:
        form = PhotoUploadForm()

    return render(request, 'upload_photo.html', {'form': form})


def edit_photo(request, pk):
    """
    Editar una foto existente.
    """
    photo = get_object_or_404(Photo, pk=pk)

    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            # después de editar, volvemos al listado
            return redirect('photo_list')
    else:
        form = PhotoUploadForm(instance=photo)

    return render(request, 'edit_photo.html', {
        'form': form,
        'photo': photo,
    })


def photo_list(request):
    """
    Listado/paginación de todas las fotos.
    """
    photos_qs = Photo.objects.all().order_by('-taken_at', '-id')
    paginator = Paginator(photos_qs, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'photos_list.html', {
        'page_obj': page_obj,
    })

def flight_list(request):
    """
    Listado simple de vuelos.
    """
    flights = Flight.objects.all().order_by('-date', 'id')
    return render(request, 'flights_list.html', {
        'flights': flights,
    })


def flight_create(request):
    """
    Crear un nuevo vuelo.
    """
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flight_list')
    else:
        form = FlightForm()

    return render(request, 'flight_form.html', {
        'form': form,
    })

def map3d_view(request):
    """
    Vista sencilla que carga la plantilla del visor 3D con Cesium.
    Los datos se obtienen vía /api/flights/ desde JavaScript.
    """
    return render(request, 'map3d.html')