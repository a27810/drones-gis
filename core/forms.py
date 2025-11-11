from django import forms
from django.core.exceptions import ValidationError
from .models import Photo
from .utils_exif import extract_gps_from_image

class PhotoUploadForm(forms.ModelForm):
    # Permitir lat/lon manual si no hay EXIF
    lat = forms.FloatField(required=False)
    lon = forms.FloatField(required=False)

    class Meta:
        model = Photo
        fields = ['flight', 'image', 'lat', 'lon', 'taken_at', 'notes']

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get('image')
        lat = cleaned.get('lat')
        lon = cleaned.get('lon')

        # Si no hay lat/lon manuales, intentar EXIF
        if (lat is None or lon is None) and image:
            try:
                image.file.seek(0)
            except Exception:
                pass
            coords = extract_gps_from_image(image.file)
            if coords:
                cleaned['lat'], cleaned['lon'] = coords

        if cleaned.get('lat') is None or cleaned.get('lon') is None:
            raise ValidationError("No se han obtenido coordenadas GPS. Indica lat/lon manualmente.")
        return cleaned
