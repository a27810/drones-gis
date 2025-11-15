from django.urls import path
from core.views import map_view

urlpatterns = [
    path("", map_view, name="map"),
]
