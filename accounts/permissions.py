from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Allows access only to the user themselves or to admin/staff users.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj == request.user
