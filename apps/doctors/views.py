"""
Views for doctor management endpoints.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Doctor
from .serializers import (
    DoctorSerializer,
    DoctorListSerializer,
    DoctorCreateUpdateSerializer,
)


class DoctorListCreateView(APIView):
    """
    GET  /api/doctors/ - List all doctors (authenticated users).
    POST /api/doctors/ - Create a new doctor.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all doctors with optional filtering."""
        doctors = Doctor.objects.select_related('created_by')

        # Optional filters
        specialization = request.query_params.get('specialization')
        if specialization:
            doctors = doctors.filter(specialization=specialization)

        is_available = request.query_params.get('is_available')
        if is_available is not None:
            doctors = doctors.filter(is_available=is_available.lower() == 'true')

        search = request.query_params.get('search')
        if search:
            doctors = doctors.filter(
                first_name__icontains=search
            ) | doctors.filter(
                last_name__icontains=search
            ) | doctors.filter(
                hospital_name__icontains=search
            )

        city = request.query_params.get('city')
        if city:
            doctors = doctors.filter(city__icontains=city)

        serializer = DoctorListSerializer(doctors, many=True)
        return Response(
            {
                'success': True,
                'count': doctors.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Create a new doctor record."""
        serializer = DoctorCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save(created_by=request.user)
            response_serializer = DoctorSerializer(doctor)
            return Response(
                {
                    'success': True,
                    'message': 'Doctor created successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to create doctor.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class DoctorDetailView(APIView):
    """
    GET    /api/doctors/<id>/ - Retrieve a specific doctor.
    PUT    /api/doctors/<id>/ - Update a specific doctor.
    DELETE /api/doctors/<id>/ - Delete a specific doctor.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Retrieve a specific doctor's details."""
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        """Update a doctor's details (full update)."""
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorCreateUpdateSerializer(doctor, data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            response_serializer = DoctorSerializer(doctor)
            return Response(
                {
                    'success': True,
                    'message': 'Doctor updated successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to update doctor.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        """Partial update of a doctor's details."""
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorCreateUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            doctor = serializer.save()
            response_serializer = DoctorSerializer(doctor)
            return Response(
                {
                    'success': True,
                    'message': 'Doctor updated successfully.',
                    'data': response_serializer.data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'success': False,
                'message': 'Failed to update doctor.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Delete a doctor record."""
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor_name = doctor.display_name
        doctor.delete()
        return Response(
            {
                'success': True,
                'message': f'Doctor "{doctor_name}" deleted successfully.',
            },
            status=status.HTTP_200_OK
        )
