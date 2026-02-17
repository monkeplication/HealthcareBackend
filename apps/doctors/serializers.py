"""
Serializers for doctor endpoints.
"""
from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model - full detail view."""
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'display_name',
            'email', 'phone', 'specialization', 'specialization_display',
            'license_number', 'years_of_experience', 'qualification',
            'bio', 'consultation_fee', 'is_available',
            'hospital_name', 'address', 'city', 'state', 'country',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_by_name', 'created_at', 'updated_at')

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None


class DoctorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for doctor list view."""
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)

    class Meta:
        model = Doctor
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'display_name',
            'email', 'phone', 'specialization', 'specialization_display',
            'license_number', 'years_of_experience', 'is_available',
            'hospital_name', 'city', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class DoctorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating doctors."""

    class Meta:
        model = Doctor
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone',
            'specialization', 'license_number', 'years_of_experience',
            'qualification', 'bio', 'consultation_fee', 'is_available',
            'hospital_name', 'address', 'city', 'state', 'country',
        )
        read_only_fields = ('id',)

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('First name cannot be blank.')
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Last name cannot be blank.')
        return value.strip()

    def validate_email(self, value):
        """Check email uniqueness excluding current instance."""
        email = value.lower()
        queryset = Doctor.objects.filter(email=email)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('A doctor with this email already exists.')
        return email

    def validate_license_number(self, value):
        """Check license number uniqueness excluding current instance."""
        queryset = Doctor.objects.filter(license_number=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('A doctor with this license number already exists.')
        return value

    def validate_years_of_experience(self, value):
        if value < 0:
            raise serializers.ValidationError('Years of experience cannot be negative.')
        if value > 70:
            raise serializers.ValidationError('Years of experience seems invalid (max 70).')
        return value

    def validate_consultation_fee(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Consultation fee cannot be negative.')
        return value

    def validate_phone(self, value):
        if value:
            cleaned = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit():
                raise serializers.ValidationError('Phone number must contain only digits and common formatting characters.')
            if len(cleaned) < 7 or len(cleaned) > 15:
                raise serializers.ValidationError('Phone number must be between 7 and 15 digits.')
        return value
