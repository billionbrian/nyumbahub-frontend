from rest_framework import permissions


class IsLandlord(permissions.BasePermission):
    """
    Permission check: User must be an authenticated landlord, or an admin/staff member.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return request.user.role == 'landlord'


class IsPropertyOwner(permissions.BasePermission):
    """
    Object-level permission: User must be the property's landlord, or an admin/staff member.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.landlord == request.user
