"""
Views for patient-doctor mapping endpoints.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import (
    MappingSerializer,
    MappingCreateSerializer,
    PatientDoctorsSerializer,
)


class MappingListCreateView(APIView):
    """
    GET  /api/mappings/ - List all patient-doctor mappings.
    POST /api/mappings/ - Assign a doctor to a patient.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all patient-doctor mappings."""
        mappings = PatientDoctorMapping.objects.select_related(
            'patient', 'doctor', 'assigned_by'
        )

        # Optional filtering
        patient_id = request.query_params.get('patient_id')
        if patient_id:
            mappings = mappings.filter(patient_id=patient_id)

        doctor_id = request.query_params.get('doctor_id')
        if doctor_id:
            mappings = mappings.filter(doctor_id=doctor_id)

        is_primary = request.query_params.get('is_primary')
        if is_primary is not None:
            mappings = mappings.filter(is_primary=is_primary.lower() == 'true')

        serializer = MappingSerializer(mappings, many=True)
        return Response(
            {
                'success': True,
                'count': mappings.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Assign a doctor to a patient."""
        serializer = MappingCreateSerializer(data=request.data)
        if serializer.is_valid():
            mapping = serializer.save(assigned_by=request.user)
            response_serializer = MappingSerializer(mapping)
            return Response(
                {
                    'success': True,
                    'message': 'Doctor assigned to patient successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to create mapping.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PatientDoctorsView(APIView):
    """
    GET /api/mappings/<patient_id>/ - Get all doctors for a specific patient.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        """Get all doctors assigned to a specific patient."""
        # Verify patient exists
        patient = get_object_or_404(Patient, pk=patient_id)

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related(
            'doctor', 'assigned_by'
        )

        serializer = PatientDoctorsSerializer(mappings, many=True)
        return Response(
            {
                'success': True,
                'patient': {
                    'id': patient.id,
                    'full_name': patient.full_name,
                },
                'count': mappings.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )


class MappingDeleteView(APIView):
    """
    DELETE /api/mappings/<id>/ - Remove a doctor from a patient.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        """Remove a specific patient-doctor mapping."""
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk)
        mapping_str = str(mapping)
        mapping.delete()
        return Response(
            {
                'success': True,
                'message': f'Mapping "{mapping_str}" removed successfully.',
            },
            status=status.HTTP_200_OK
        )

    def get(self, request, pk):
        """Get details of a specific mapping."""
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk)
        serializer = MappingSerializer(mapping)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )
