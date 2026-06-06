from rest_framework import serializers
from .models import Property
from accounts.serializers import UserSerializer


class PropertySerializer(serializers.ModelSerializer):
    landlord = UserSerializer(read_only=True)
    
    class Meta:
        model = Property
        fields = ['id', 'landlord', 'title', 'description', 'location', 'rent_amount', 
                  'bedrooms', 'bathrooms', 'property_type', 'available', 'created_at']
        read_only_fields = ['id', 'landlord', 'created_at']
    
    def validate_rent_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Rent amount must be greater than zero.")
        return value
    
    def validate_bedrooms(self, value):
        if value <= 0:
            raise serializers.ValidationError("Number of bedrooms must be greater than zero.")
        return value
    
    def validate_bathrooms(self, value):
        if value <= 0:
            raise serializers.ValidationError("Number of bathrooms must be greater than zero.")
        return value
