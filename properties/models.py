from django.db import models
from accounts.models import User


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('townhouse', 'Townhouse'),
        ('villa', 'Villa'),
    ]
    
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return f"{self.title} - {self.location} (KES {self.rent_amount})"
