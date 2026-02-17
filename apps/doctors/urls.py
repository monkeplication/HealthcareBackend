"""
URL patterns for doctor endpoints.
"""
from django.urls import path
from .views import DoctorListCreateView, DoctorDetailView

urlpatterns = [
    path('doctors/', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
]
