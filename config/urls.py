from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# DRF router
from rest_framework.routers import DefaultRouter

# ViewSets y vista del formulario
from core.views import (
    FlightViewSet,
    PhotoViewSet,
    ZoneViewSet,
    upload_photo,
)

# --- Router API ---
router = DefaultRouter()
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'zones', ZoneViewSet, basename='zone')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='map.html'), name='home'),
    path('upload/photo/', upload_photo, name='upload_photo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
