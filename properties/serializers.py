from decimal import Decimal
from rest_framework import serializers
from .models import Property, PropertyImage
from accounts.serializers import PublicUserSerializer
from .services.geocoding import reverse_geocode


class PropertyImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'url', 'is_primary', 'caption', 'created_at']
        read_only_fields = ['id', 'created_at', 'url']

    def get_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url or ''


class PropertySerializer(serializers.ModelSerializer):
    landlord = PublicUserSerializer(read_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    image = serializers.FileField(required=False, allow_null=True)
    image_url = serializers.URLField(max_length=500, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'landlord', 'title', 'description', 'location', 
            'latitude', 'longitude', 'rent_amount', 'bedrooms', 
            'bathrooms', 'property_type', 'status', 'available',
            'image', 'image_url', 'images', 'primary_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'landlord', 'created_at', 'updated_at', 'images', 'primary_image']

    def get_primary_image(self, obj):
        url = obj.primary_image_url
        if not url:
            return None
        request = self.context.get('request')
        if request and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url

    
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

    def validate_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value

    def validate(self, attrs):
        # On property creation, coordinates must be provided and confirmed
        if self.instance is None:
            lat = attrs.get('latitude')
            lon = attrs.get('longitude')
            if lat is None or lon is None:
                raise serializers.ValidationError({
                    "coordinates": "Both latitude and longitude are required to confirm the property location."
                })
        else:
            # On update, if either coordinate is passed, check pair consistency
            if 'latitude' in attrs or 'longitude' in attrs:
                new_lat = attrs.get('latitude', self.instance.latitude)
                new_lon = attrs.get('longitude', self.instance.longitude)
                if (new_lat is None) != (new_lon is None):
                    raise serializers.ValidationError({
                        "coordinates": "Both latitude and longitude must be provided together."
                    })
        return attrs

    def create(self, validated_data):
        lat = validated_data.get('latitude')
        lon = validated_data.get('longitude')
        if lat is not None and lon is not None:
            # Reverse geocode coordinates to populate human-readable location
            validated_data['location'] = reverse_geocode(lat, lon)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_lat = validated_data.get('latitude')
        new_lon = validated_data.get('longitude')

        # Check if coordinates have changed
        if new_lat is not None and new_lon is not None:
            coords_changed = (
                instance.latitude is None or
                instance.longitude is None or
                Decimal(str(instance.latitude)) != Decimal(str(new_lat)) or
                Decimal(str(instance.longitude)) != Decimal(str(new_lon))
            )
            if coords_changed:
                validated_data['location'] = reverse_geocode(new_lat, new_lon)
            else:
                # If coordinates are unchanged, do not re-geocode
                validated_data.pop('location', None)
        elif 'location' in validated_data and instance.latitude is not None and instance.longitude is not None:
            # Disregard client-supplied location string when coordinates are authoritative
            validated_data.pop('location')

        return super().update(instance, validated_data)
