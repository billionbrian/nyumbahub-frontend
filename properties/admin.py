from django.contrib import admin
from .models import Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'rent_amount', 'bedrooms', 'bathrooms', 'property_type', 'available', 'landlord', 'created_at']
    list_filter = ['property_type', 'available', 'created_at']
    search_fields = ['title', 'location', 'landlord__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('landlord', 'title', 'description', 'location', 'image', 'image_url')
        }),
        ('Property Details', {
            'fields': ('rent_amount', 'bedrooms', 'bathrooms', 'property_type', 'status', 'available')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'is_primary', 'image', 'image_url', 'created_at']
    list_filter = ['is_primary', 'created_at']


