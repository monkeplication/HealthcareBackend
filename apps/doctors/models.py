"""
Doctor model for the healthcare application.
"""
from django.db import models
from django.conf import settings


class Doctor(models.Model):
    """
    Model representing a doctor in the healthcare system.
    """

    SPECIALIZATION_CHOICES = [
        ('general', 'General Practitioner'),
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('endocrinology', 'Endocrinology'),
        ('gastroenterology', 'Gastroenterology'),
        ('hematology', 'Hematology'),
        ('infectious_disease', 'Infectious Disease'),
        ('internal_medicine', 'Internal Medicine'),
        ('nephrology', 'Nephrology'),
        ('neurology', 'Neurology'),
        ('obstetrics_gynecology', 'Obstetrics & Gynecology'),
        ('oncology', 'Oncology'),
        ('ophthalmology', 'Ophthalmology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('pulmonology', 'Pulmonology'),
        ('radiology', 'Radiology'),
        ('rheumatology', 'Rheumatology'),
        ('surgery', 'Surgery'),
        ('urology', 'Urology'),
        ('other', 'Other'),
    ]

    # Core fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    license_number = models.CharField(max_length=100, unique=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    # Address / hospital
    hospital_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Ownership & timestamps
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_doctors',
        help_text='User who created this doctor record.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctors'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['specialization']),
            models.Index(fields=['license_number']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f'Dr. {self.first_name} {self.last_name} ({self.get_specialization_display()})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def display_name(self):
        return f'Dr. {self.first_name} {self.last_name}'
