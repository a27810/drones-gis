from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from core.views import (
    FlightViewSet,
    PhotoViewSet,
    ZoneViewSet,
    home,
    map_view,
    upload_photo,
    edit_photo,
    photo_list,
    flight_list,
    flight_create,
)

router = DefaultRouter()
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'zones', ZoneViewSet, basename='zone')

urlpatterns = [
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include(router.urls)),

    # Vistas HTML
    path('', home, name='home'),
    path('map/', map_view, name='map'),
    path('upload/photo/', upload_photo, name='upload_photo'),
    path('photos/', photo_list, name='photo_list'),
    path('photos/<int:pk>/edit/', edit_photo, name='edit_photo'),
    path('flights/', flight_list, name='flight_list'),
    path('flights/new/', flight_create, name='flight_create'),

]

# servir ficheros de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
