from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import JsonResponse
from django.urls import path
from django import forms
from .models import User
from .location_models import City, District, Neighborhood
import locale


# Turkish alphabetical ordering function
def turkish_sort_key(text):
    """Convert Turkish characters for proper alphabetical sorting"""
    if not text:
        return ''
    
    # Turkish alphabet order mapping - correct order: C before Ç, S before Ş
    turkish_order = {
        'a': 'a', 'b': 'b', 'c': 'c', 'ç': 'c~', 'd': 'd', 'e': 'e', 'f': 'f',
        'g': 'g', 'ğ': 'g~', 'h': 'h', 'ı': 'i', 'i': 'i~', 'j': 'j', 'k': 'k',
        'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'ö': 'o~', 'p': 'p', 'r': 'r',
        's': 's', 'ş': 's~', 't': 't', 'u': 'u', 'ü': 'u~', 'v': 'v', 'y': 'y', 'z': 'z',
        'A': 'a', 'B': 'b', 'C': 'c', 'Ç': 'c~', 'D': 'd', 'E': 'e', 'F': 'f',
        'G': 'g', 'Ğ': 'g~', 'H': 'h', 'I': 'i', 'İ': 'i~', 'J': 'j', 'K': 'k',
        'L': 'l', 'M': 'm', 'N': 'n', 'O': 'o', 'Ö': 'o~', 'P': 'p', 'R': 'r',
        'S': 's', 'Ş': 's~', 'T': 't', 'U': 'u', 'Ü': 'u~', 'V': 'v', 'Y': 'y', 'Z': 'z'
    }
    
    result = ''
    for char in text.lower():
        result += turkish_order.get(char, char)
    return result


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'city', 'ilce', 'mahalle', 'finansal_kod_numarasi', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'city', 'ilce', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'city', 'ilce', 'mahalle', 'finansal_kod_numarasi')
    ordering = ('email',)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        from django import forms
        
        # Override individual field labels and widgets
        if db_field.name == 'first_name':
            kwargs['label'] = 'Adı'
        elif db_field.name == 'last_name':
            kwargs['label'] = 'Soyadı'
        elif db_field.name == 'phone':
            kwargs['label'] = 'Telefon'
        elif db_field.name == 'city':
            kwargs['label'] = 'Şehir'
            # Get the default field first
            field = super().formfield_for_dbfield(db_field, request, **kwargs)
            # Get all cities and sort them properly
            cities = City.objects.all()
            sorted_cities = sorted(cities, key=lambda x: turkish_sort_key(x.name))
            choices = [('', 'Şehir seçin')]
            choices.extend([(city.name, city.name) for city in sorted_cities])
            # Update the widget with choices and onchange event
            field.widget = forms.Select(
                choices=choices,
                attrs={'id': 'id_city', 'onchange': 'updateDistricts()'}
            )
            return field
        elif db_field.name == 'ilce':
            kwargs['label'] = 'İlçe'
            # Get the default field first
            field = super().formfield_for_dbfield(db_field, request, **kwargs)
            
            # If we're editing an existing user, populate districts
            choices = [('', 'İlçe seçin')]
            if hasattr(request, 'resolver_match') and request.resolver_match.kwargs.get('object_id'):
                try:
                    user_id = request.resolver_match.kwargs['object_id']
                    user = User.objects.get(pk=user_id)
                    if user.city:
                        city = City.objects.get(name=user.city)
                        districts = District.objects.filter(city=city)
                        sorted_districts = sorted(districts, key=lambda x: turkish_sort_key(x.name))
                        choices.extend([(d.name, d.name) for d in sorted_districts])
                except (User.DoesNotExist, City.DoesNotExist):
                    pass
            
            field.widget = forms.Select(
                choices=choices,
                attrs={'id': 'id_ilce', 'onchange': 'updateNeighborhoods()'}
            )
            return field
        elif db_field.name == 'mahalle':
            kwargs['label'] = 'Mahalle'
            # Get the default field first
            field = super().formfield_for_dbfield(db_field, request, **kwargs)
            
            # If we're editing an existing user, populate neighborhoods
            choices = [('', 'Mahalle seçin')]
            if hasattr(request, 'resolver_match') and request.resolver_match.kwargs.get('object_id'):
                try:
                    user_id = request.resolver_match.kwargs['object_id']
                    user = User.objects.get(pk=user_id)
                    if user.city and user.ilce:
                        city = City.objects.get(name=user.city)
                        district = District.objects.get(name=user.ilce, city=city)
                        neighborhoods = Neighborhood.objects.filter(district=district)
                        sorted_neighborhoods = sorted(neighborhoods, key=lambda x: turkish_sort_key(x.name))
                        choices.extend([(n.name, n.name) for n in sorted_neighborhoods])
                except (User.DoesNotExist, City.DoesNotExist, District.DoesNotExist):
                    pass
            
            field.widget = forms.Select(
                choices=choices,
                attrs={'id': 'id_mahalle'}
            )
            return field
        elif db_field.name == 'finansal_kod_numarasi':
            kwargs['label'] = 'Finansal Kod Numarası'
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'city', 'ilce', 'mahalle', 'finansal_kod_numarasi', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'city', 'ilce', 'mahalle', 'finansal_kod_numarasi', 'phone', 'role'),
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
    print(f"Getting districts for city: {city_name}")
    
    if city_name:
        try:
            city = City.objects.get(name=city_name)
            districts = District.objects.filter(city=city)
            print(f"Found {districts.count()} districts for {city_name}")
            
            # Sort districts using Turkish alphabetical order
            sorted_districts = sorted(districts, key=lambda x: turkish_sort_key(x.name))
            data = {
                'districts': [{'name': d.name, 'value': d.name} for d in sorted_districts]
            }
            print(f"Returning districts: {[d.name for d in sorted_districts]}")
        except City.DoesNotExist:
            print(f"City '{city_name}' not found")
            data = {'districts': []}
    else:
        print("No city name provided")
        data = {'districts': []}
    
    return JsonResponse(data)


def get_neighborhoods_view(request):
    city_name = request.GET.get('city_name')
    district_name = request.GET.get('district_name')
    print(f"Getting neighborhoods for district: {district_name} in city: {city_name}")
    
    if city_name and district_name:
        try:
            city = City.objects.get(name=city_name)
            district = District.objects.get(name=district_name, city=city)
            neighborhoods = Neighborhood.objects.filter(district=district)
            print(f"Found {neighborhoods.count()} neighborhoods for {district_name}")
            
            # Sort neighborhoods using Turkish alphabetical order
            sorted_neighborhoods = sorted(neighborhoods, key=lambda x: turkish_sort_key(x.name))
            data = {
                'neighborhoods': [{'name': n.name, 'value': n.name} for n in sorted_neighborhoods]
            }
            print(f"Returning neighborhoods: {[n.name for n in sorted_neighborhoods[:5]]}...")  # Show first 5
        except (City.DoesNotExist, District.DoesNotExist) as e:
            print(f"Error: {e}")
            data = {'neighborhoods': []}
    else:
        print("Missing city or district name")
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
        path('get-districts/', get_districts_view, name='admin_get_districts'),
        path('get-neighborhoods/', get_neighborhoods_view, name='admin_get_neighborhoods'),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls