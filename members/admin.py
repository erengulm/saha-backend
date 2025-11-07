from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .location_models import City, District, Neighborhood


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'city', 'ilce', 'mahalle', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'city', 'ilce', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'city', 'ilce', 'mahalle')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'city', 'ilce', 'mahalle', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'city', 'ilce', 'mahalle', 'phone', 'role'),
        }),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'created_at')
    list_filter = ('city',)
    search_fields = ('name', 'city__name')
    ordering = ('city__name', 'name')


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'city', 'created_at')
    list_filter = ('district__city',)
    search_fields = ('name', 'district__name', 'district__city__name')
    ordering = ('district__city__name', 'district__name', 'name')
    
    def city(self, obj):
        return obj.district.city.name
    city.short_description = 'City'


admin.site.register(User, CustomUserAdmin)