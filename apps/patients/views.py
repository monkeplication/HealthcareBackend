"""
Views for patient management endpoints.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Patient
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientCreateUpdateSerializer,
)


class PatientListCreateView(APIView):
    """
    GET  /api/patients/ - List all patients created by authenticated user.
    POST /api/patients/ - Create a new patient.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all patients created by the authenticated user."""
        patients = Patient.objects.filter(created_by=request.user).select_related('created_by')

        # Optional filtering
        search = request.query_params.get('search')
        if search:
            patients = patients.filter(
                first_name__icontains=search
            ) | patients.filter(
                last_name__icontains=search
            ) | patients.filter(
                email__icontains=search
            )

        gender = request.query_params.get('gender')
        if gender:
            patients = patients.filter(gender=gender)

        serializer = PatientListSerializer(patients, many=True)
        return Response(
            {
                'success': True,
                'count': patients.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Create a new patient record."""
        serializer = PatientCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save(created_by=request.user)
            response_serializer = PatientSerializer(patient)
            return Response(
                {
                    'success': True,
                    'message': 'Patient created successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to create patient.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PatientDetailView(APIView):
    """
    GET    /api/patients/<id>/ - Retrieve a specific patient.
    PUT    /api/patients/<id>/ - Update a specific patient.
    DELETE /api/patients/<id>/ - Delete a specific patient.
    """
    permission_classes = [IsAuthenticated]

    def _get_patient(self, pk, user):
        """Helper to retrieve a patient owned by the user."""
        return get_object_or_404(Patient, pk=pk, created_by=user)

    def get(self, request, pk):
        """Retrieve a specific patient's details."""
        patient = self._get_patient(pk, request.user)
        serializer = PatientSerializer(patient)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        """Update a patient's details (full update)."""
        patient = self._get_patient(pk, request.user)
        serializer = PatientCreateUpdateSerializer(patient, data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            response_serializer = PatientSerializer(patient)
            return Response(
                {
                    'success': True,
                    'message': 'Patient updated successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to update patient.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        """Partial update of a patient's details."""
        patient = self._get_patient(pk, request.user)
        serializer = PatientCreateUpdateSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            patient = serializer.save()
            response_serializer = PatientSerializer(patient)
            return Response(
                {
                    'success': True,
                    'message': 'Patient updated successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to update patient.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Delete a patient record."""
        patient = self._get_patient(pk, request.user)
        patient_name = patient.full_name
        patient.delete()
        return Response(
            {
                'success': True,
                'message': f'Patient "{patient_name}" deleted successfully.',
            },
            status=status.HTTP_200_OK
        )
