"""
Admin configuration for doctors app.
"""
from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'email', 'specialization', 'license_number', 'is_available', 'created_at')
    list_filter = ('specialization', 'is_available', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'license_number', 'hospital_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'license_number', 'years_of_experience', 'qualification', 'bio', 'consultation_fee', 'is_available')
        }),
        ('Hospital & Address', {
            'fields': ('hospital_name', 'address', 'city', 'state', 'country')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
