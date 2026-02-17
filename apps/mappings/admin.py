"""
Admin configuration for mappings app.
"""
from django.contrib import admin
from .models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'is_primary', 'assigned_by', 'assigned_at')
    list_filter = ('is_primary', 'assigned_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    ordering = ('-assigned_at',)
    readonly_fields = ('assigned_at', 'updated_at')
