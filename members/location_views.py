# members/location_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .location_models import City, District, Neighborhood


@api_view(['GET'])
def get_cities(request):
    """Get all cities"""
    try:
        cities = City.objects.all().values_list('name', flat=True).order_by('name')
        city_list = list(cities)
        
        # Ensure proper UTF-8 encoding
        city_list = [str(c) for c in city_list]
        
        response = Response({
            'success': True,
            'cities': city_list
        }, status=status.HTTP_200_OK)
        
        # Explicitly set content type for UTF-8
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Şehir verileri alınırken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_districts(request, city_name):
    """Get districts for a specific city"""
    try:
        city = City.objects.get(name=city_name)
        districts = city.districts.all().values_list('name', flat=True).order_by('name')
        district_list = list(districts)
        
        # Ensure proper UTF-8 encoding
        district_list = [str(d) for d in district_list]
        
        response = Response({
            'success': True,
            'city': city_name,
            'districts': district_list
        }, status=status.HTTP_200_OK)
        
        # Explicitly set content type for UTF-8
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except City.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Şehir bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'İlçe verileri alınırken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_neighborhoods(request, city_name, district_name):
    """Get neighborhoods for a specific district in a city"""
    try:
        city = City.objects.get(name=city_name)
        district = city.districts.get(name=district_name)
        neighborhoods = district.neighborhoods.all().values_list('name', flat=True).order_by('name')
        neighborhood_list = list(neighborhoods)
        
        # Ensure proper UTF-8 encoding
        neighborhood_list = [str(n) for n in neighborhood_list]
        
        response = Response({
            'success': True,
            'city': city_name,
            'district': district_name,
            'neighborhoods': neighborhood_list
        }, status=status.HTTP_200_OK)
        
        # Explicitly set content type for UTF-8
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except City.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Şehir bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except District.DoesNotExist:
        return Response({
            'success': False,
            'error': 'İlçe bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Mahalle verileri alınırken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_all_locations(request):
    """Get all location data in hierarchical structure"""
    try:
        locations = {}
        
        for city in City.objects.prefetch_related('districts__neighborhoods').all():
            city_districts = {}
            
            for district in city.districts.all():
                district_neighborhoods = list(
                    district.neighborhoods.all().values_list('name', flat=True).order_by('name')
                )
                city_districts[district.name] = district_neighborhoods
            
            locations[city.name] = city_districts
        
        return Response({
            'success': True,
            'locations': locations
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Konum verileri alınırken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)