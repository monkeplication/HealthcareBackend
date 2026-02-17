"""
Patient-Doctor mapping model for the healthcare application.
"""
from django.db import models
from django.conf import settings


class PatientDoctorMapping(models.Model):
    """
    Model representing the many-to-many relationship
    between patients and doctors.
    """

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        help_text='The patient being assigned a doctor.'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        help_text='The doctor being assigned to the patient.'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_mappings',
        help_text='User who created this mapping.'
    )
    notes = models.TextField(blank=True, null=True, help_text='Any notes about this assignment.')
    is_primary = models.BooleanField(
        default=False,
        help_text='Whether this doctor is the primary care physician for the patient.'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_doctor_mappings'
        unique_together = ('patient', 'doctor')
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['doctor']),
            models.Index(fields=['assigned_by']),
        ]

    def __str__(self):
        return f'{self.patient.full_name} → Dr. {self.doctor.full_name}'
