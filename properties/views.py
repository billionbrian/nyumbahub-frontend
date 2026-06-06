from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property
from .serializers import PropertySerializer


class IsLandlord(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'landlord'


class IsPropertyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.landlord == request.user


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsLandlord]
        else:
            permission_classes = [permissions.IsAuthenticated, IsLandlord, IsPropertyOwner]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)
