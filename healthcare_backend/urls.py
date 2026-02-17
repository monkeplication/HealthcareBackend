"""
URL configuration for healthcare_backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/', include('apps.patients.urls')),
    path('api/', include('apps.doctors.urls')),
    path('api/', include('apps.mappings.urls')),
]
