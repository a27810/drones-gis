import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
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


def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    # Eliminar archivo físico del disco
    if photo.image:
        photo.image.delete(save=False)

    # Eliminar entrada en base de datos
    photo.delete()

    messages.success(request, "Foto eliminada correctamente.")
    return redirect('photo_list')
    

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

def export_single_flight_geojson(request, flight_id):
    """
    Exporta SOLO la ruta de un vuelo en formato GeoJSON.
    """
    from .models import Flight

    flight = Flight.objects.filter(id=flight_id).first()
    if not flight or not flight.path_geojson:
        return JsonResponse({"error": "Vuelo no encontrado o sin ruta"}, status=404)

    # Construimos Feature GeoJSON estándar
    feature = {
        "type": "Feature",
        "properties": {
            "name": flight.name,
            "drone_model": flight.drone_model,
            "date": str(flight.date) if flight.date else None
        },
        "geometry": flight.path_geojson
    }

    response = HttpResponse(
        json.dumps(feature, indent=2),
        content_type="application/geo+json"
    )
    response["Content-Disposition"] = f'attachment; filename="flight_{flight.id}.geojson"'

    return response

def map3d_view(request):
    """
    Vista sencilla que carga la plantilla del visor 3D con Cesium.
    Los datos se obtienen vía /api/flights/ desde JavaScript.
    """
    return render(request, 'map3d.html')

def export_flights_geojson(request):
    """
    Exporta todos los vuelos con ruta (path_geojson) en formato GeoJSON estándar.
    Cada vuelo se convierte en un Feature con geometría LineString y propiedades
    como id, nombre, modelo de dron, fecha y número de fotos asociadas.
    """
    features = []

    for flight in Flight.objects.all().order_by('-date', 'id'):
        gj = flight.path_geojson
        if not gj:
            # Si el vuelo no tiene ruta, lo saltamos
            continue

        line = None

        # Aceptamos:
        #  - {"type": "LineString", "coordinates": [...]}
        #  - {"type": "Feature", "geometry": {"type": "LineString", ...}}
        if isinstance(gj, dict):
            if gj.get('type') == 'LineString':
                line = gj
            elif gj.get('type') == 'Feature':
                geom = gj.get('geometry') or {}
                if geom.get('type') == 'LineString':
                    line = geom

        # Si no hemos podido obtener una LineString válida, lo saltamos
        if not line or not isinstance(line.get('coordinates'), list) or not line['coordinates']:
            continue

        feature = {
            "type": "Feature",
            "properties": {
                "id": flight.id,
                "name": flight.name,
                "drone_model": flight.drone_model,
                "date": flight.date.isoformat() if flight.date else None,
                "num_photos": flight.photos.count(),
            },
            "geometry": line,
        }
        features.append(feature)

    data = {
        "type": "FeatureCollection",
        "features": features,
    }

    # Devolvemos GeoJSON bonito e identificable como tal
    return JsonResponse(
        data,
        json_dumps_params={"indent": 2},
        content_type="application/geo+json"
    )

def delete_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    flight.delete()
    messages.success(request, "Vuelo eliminado correctamente.")
    return redirect('flight_list')


def export_photos_geojson(request):
    """
    Exporta las fotos como un FeatureCollection GeoJSON.
    Opcionalmente puede filtrar por ?flight=<id>.
    """
    flight_id = request.GET.get('flight')

    photos_qs = Photo.objects.all()
    if flight_id:
        photos_qs = photos_qs.filter(flight_id=flight_id)

    features = []
    for p in photos_qs:
        # Solo fotos con coordenadas válidas
        if p.lat is None or p.lon is None:
            continue

        image_url = request.build_absolute_uri(p.image.url) if p.image else None

        features.append({
            "type": "Feature",
            "properties": {
                "id": p.id,
                "flight_id": p.flight_id,
                "flight_name": p.flight.name if p.flight else None,
                "taken_at": p.taken_at.isoformat() if p.taken_at else None,
                "notes": p.notes,
                "image_url": image_url,
            },
            "geometry": {
                "type": "Point",
                # GeoJSON siempre va [lon, lat]
                "coordinates": [p.lon, p.lat],
            },
        })

    data = {
        "type": "FeatureCollection",
        "features": features,
    }

    response = JsonResponse(data)
    response["Content-Type"] = "application/geo+json"
    response["Content-Disposition"] = 'attachment; filename="photos.geojson"'
    return response

def edit_flight_path(request, flight_id):
    """Editor visual de rutas con Leaflet."""
    flight = get_object_or_404(Flight, id=flight_id)
    return render(request, "edit_flight_path.html", {"flight": flight})


def api_save_flight_path(request, flight_id):
    """Guarda el GeoJSON enviado desde Leaflet."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    flight = get_object_or_404(Flight, id=flight_id)

    try:
        data = json.loads(request.body)
        geojson = data.get("geojson")

        if not geojson:
            return JsonResponse({"error": "No se recibió GeoJSON"}, status=400)

        flight.path_geojson = geojson
        flight.save()

        return JsonResponse({"status": "ok"})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

