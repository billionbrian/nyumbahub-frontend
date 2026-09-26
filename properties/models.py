from django.db import models
from accounts.models import User


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('single', 'Single'),
        ('bedsitter', 'Bedsitter'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('three_bedroom', 'Three Bedroom'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
    ]
    
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    available = models.BooleanField(default=True)  # Kept for backwards compatibility
    image = models.FileField(upload_to='property_images/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return f"{self.title} - {self.location} (KES {self.rent_amount})"

    @property
    def primary_image_url(self):
        """Returns the primary image URL from related images or fallback to property.image / image_url"""
        primary = self.images.filter(is_primary=True).first() or self.images.first()
        if primary and primary.get_url():
            return primary.get_url()
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='property_images/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'

    def __str__(self):
        return f"Image for {self.property.title} ({'Primary' if self.is_primary else 'Gallery'})"

    def get_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

