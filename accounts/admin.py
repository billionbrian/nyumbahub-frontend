from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'created_at', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'created_at')}),
    )
    
    readonly_fields = ['created_at']

