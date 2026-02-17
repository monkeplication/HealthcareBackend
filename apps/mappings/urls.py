"""
URL patterns for patient-doctor mapping endpoints.
"""
from django.urls import path
from .views import MappingListCreateView, PatientDoctorsView, MappingDeleteView

urlpatterns = [
    path('mappings/', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('mappings/<int:patient_id>/', PatientDoctorsView.as_view(), name='patient-doctors'),
    path('mappings/detail/<int:pk>/', MappingDeleteView.as_view(), name='mapping-detail-delete'),
]
