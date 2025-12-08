from django import forms
from django.core.exceptions import ValidationError
from .models import Photo, Flight
from .utils_exif import extract_gps_from_image


def dms_to_decimal(dms, ref):
    """
    Convierte coordenadas EXIF (DMS) a decimal.
    dms viene como una tupla: (deg, min, sec)
    ref es 'N', 'S', 'E', 'W'
    """
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])

        value = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Longitud Oeste y latitud Sur deben ser negativas
        if ref in ['S', 'W']:
            value = -value

        return value
    except:
        return None


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['flight', 'image', 'lat', 'lon', 'taken_at', 'notes']

    # Permitir coordenadas negativas manualmente
    lat = forms.FloatField(required=False)
    lon = forms.FloatField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        lat = cleaned_data.get("lat")
        lon = cleaned_data.get("lon")

        # Si lat/lon vienen con coma, convertirlas
        if isinstance(lat, str):
            lat = float(lat.replace(",", "."))
            cleaned_data["lat"] = lat

        if isinstance(lon, str):
            lon = float(lon.replace(",", "."))
            cleaned_data["lon"] = lon

        # Si el usuario NO introduce coordenadas → usar EXIF automáticamente
        if image and (lat is None or lon is None):
            gps = extract_gps_from_image(image)
            print("DEBUG EXIF → gps devuelto:", gps)

            if gps:
                cleaned_data["lat"] = gps.get("lat")
                cleaned_data["lon"] = gps.get("lon")

        # Validación final de rangos
        lat = cleaned_data.get("lat")
        lon = cleaned_data.get("lon")

        if lat is None or lon is None:
            raise ValidationError("Debe introducir coordenadas o incluir una imagen con EXIF GPS válido.")

        if not (-90 <= lat <= 90):
            raise ValidationError("Latitud fuera de rango (-90 a 90).")

        if not (-180 <= lon <= 180):
            raise ValidationError("Longitud fuera de rango (-180 a 180).")

        return cleaned_data


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['name', 'drone_model', 'date', 'path_geojson']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'path_geojson': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Nombre del vuelo',
            'drone_model': 'Modelo de dron',
            'date': 'Fecha',
            'path_geojson': 'Ruta (GeoJSON opcional)',
        }
        help_texts = {
            'path_geojson': 'Opcional: LineString o Feature en formato GeoJSON para representar la ruta.',
        }
