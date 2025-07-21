from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'city', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'city', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'city')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('city', 'role')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'city', 'role')}),
    )


admin.site.register(User, CustomUserAdmin)