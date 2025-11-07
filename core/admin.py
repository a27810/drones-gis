from django.contrib import admin
from .models import Flight, Photo, Zone
admin.register(Flight)(admin.ModelAdmin)
admin.register(Photo)(admin.ModelAdmin)
admin.register(Zone)(admin.ModelAdmin)
