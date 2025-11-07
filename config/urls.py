from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from core.views import FlightViewSet, PhotoViewSet, ZoneViewSet
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'flights', FlightViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'zones', ZoneViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='map.html'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
