from django.contrib import admin
from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'rent_amount', 'bedrooms', 'bathrooms', 'property_type', 'available', 'landlord', 'created_at']
    list_filter = ['property_type', 'available', 'created_at']
    search_fields = ['title', 'location', 'landlord__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('landlord', 'title', 'description', 'location')
        }),
        ('Property Details', {
            'fields': ('rent_amount', 'bedrooms', 'bathrooms', 'property_type', 'available')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

