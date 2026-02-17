"""
Serializers for patient-doctor mapping endpoints.
"""
from rest_framework import serializers
from .models import PatientDoctorMapping
from apps.patients.serializers import PatientListSerializer
from apps.doctors.serializers import DoctorListSerializer


class MappingSerializer(serializers.ModelSerializer):
    """Full serializer for patient-doctor mappings with nested detail."""
    patient_detail = PatientListSerializer(source='patient', read_only=True)
    doctor_detail = DoctorListSerializer(source='doctor', read_only=True)
    assigned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id', 'patient', 'patient_detail',
            'doctor', 'doctor_detail',
            'assigned_by', 'assigned_by_name',
            'notes', 'is_primary',
            'assigned_at', 'updated_at',
        )
        read_only_fields = ('id', 'assigned_by', 'assigned_by_name', 'assigned_at', 'updated_at')

    def get_assigned_by_name(self, obj):
        return obj.assigned_by.name if obj.assigned_by else None


class MappingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new patient-doctor mapping."""

    class Meta:
        model = PatientDoctorMapping
        fields = ('id', 'patient', 'doctor', 'notes', 'is_primary')
        read_only_fields = ('id',)

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Check for duplicate mapping (excluding current instance for updates)
        queryset = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                f'Doctor "{doctor.display_name}" is already assigned to patient "{patient.full_name}".'
            )

        return attrs


class PatientDoctorsSerializer(serializers.ModelSerializer):
    """Serializer for listing all doctors for a specific patient."""
    doctor_detail = DoctorListSerializer(source='doctor', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id', 'doctor', 'doctor_detail',
            'notes', 'is_primary', 'assigned_at',
        )
        read_only_fields = ('id', 'assigned_at')
