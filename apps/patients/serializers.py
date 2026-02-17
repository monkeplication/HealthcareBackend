"""
Serializers for patient endpoints.
"""
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model - full detail view."""
    full_name = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            'id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'gender',
            'blood_group', 'allergies', 'medical_history',
            'current_medications', 'emergency_contact_name',
            'emergency_contact_phone', 'address', 'city',
            'state', 'country', 'postal_code',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_by_name', 'created_at', 'updated_at')

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None

    def validate_date_of_birth(self, value):
        """Ensure date of birth is not in the future."""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value

    def validate_phone(self, value):
        """Basic phone number validation."""
        if value:
            # Remove common formatting characters
            cleaned = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit():
                raise serializers.ValidationError('Phone number must contain only digits and common formatting characters.')
            if len(cleaned) < 7 or len(cleaned) > 15:
                raise serializers.ValidationError('Phone number must be between 7 and 15 digits.')
        return value

    def validate_email(self, value):
        """Validate email format (already handled by EmailField)."""
        if value:
            return value.lower()
        return value


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for patient list view."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = (
            'id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'gender',
            'blood_group', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class PatientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating patients."""

    class Meta:
        model = Patient
        fields = (
            'id', 'first_name', 'last_name',
            'email', 'phone', 'date_of_birth', 'gender',
            'blood_group', 'allergies', 'medical_history',
            'current_medications', 'emergency_contact_name',
            'emergency_contact_phone', 'address', 'city',
            'state', 'country', 'postal_code',
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

    def validate_date_of_birth(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        return value

    def validate_phone(self, value):
        if value:
            cleaned = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit():
                raise serializers.ValidationError('Phone number must contain only digits and common formatting characters.')
            if len(cleaned) < 7 or len(cleaned) > 15:
                raise serializers.ValidationError('Phone number must be between 7 and 15 digits.')
        return value

    def validate_email(self, value):
        if value:
            return value.lower()
        return value
