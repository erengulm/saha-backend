from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import JsonResponse
from django.urls import path
from .models import User
from .location_models import City, District, Neighborhood


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'city', 'ilce', 'mahalle', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'city', 'ilce', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'city', 'ilce', 'mahalle')
    ordering = ('email',)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Override individual field labels and widgets
        if db_field.name == 'city':
            kwargs['label'] = 'Şehir'
        elif db_field.name == 'ilce':
            kwargs['label'] = 'İlçe'
        elif db_field.name == 'mahalle':
            kwargs['label'] = 'Mahalle'
        elif db_field.name == 'phone':
            kwargs['label'] = 'Telefon'
        return super().formfield_for_dbfield(db_field, request, **kwargs)

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

    class Media:
        js = ('admin/js/user_admin.js',)
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


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


# Admin views for AJAX dropdowns
def get_districts_view(request):
    city_name = request.GET.get('city_name')
    if city_name:
        try:
            city = City.objects.get(name=city_name)
            districts = District.objects.filter(city=city).order_by('name')
            data = {
                'districts': [{'name': d.name, 'value': d.name} for d in districts]
            }
        except City.DoesNotExist:
            data = {'districts': []}
    else:
        data = {'districts': []}
    return JsonResponse(data)


def get_neighborhoods_view(request):
    city_name = request.GET.get('city_name')
    district_name = request.GET.get('district_name')
    if city_name and district_name:
        try:
            city = City.objects.get(name=city_name)
            district = District.objects.get(name=district_name, city=city)
            neighborhoods = Neighborhood.objects.filter(district=district).order_by('name')
            data = {
                'neighborhoods': [{'name': n.name, 'value': n.name} for n in neighborhoods]
            }
        except (City.DoesNotExist, District.DoesNotExist):
            data = {'neighborhoods': []}
    else:
        data = {'neighborhoods': []}
    return JsonResponse(data)


# Register admin URLs
from django.urls import path

admin_urls = [
    path('get-districts/', get_districts_view, name='get_districts'),
    path('get-neighborhoods/', get_neighborhoods_view, name='get_neighborhoods'),
]

# Add custom URLs to admin
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('get-districts/', get_districts_view, name='get_districts'),
        path('get-neighborhoods/', get_neighborhoods_view, name='get_neighborhoods'),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls