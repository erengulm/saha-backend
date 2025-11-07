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
        return Response({
            'success': True,
            'cities': list(cities)
        }, status=status.HTTP_200_OK)
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
        return Response({
            'success': True,
            'city': city_name,
            'districts': list(districts)
        }, status=status.HTTP_200_OK)
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
        return Response({
            'success': True,
            'city': city_name,
            'district': district_name,
            'neighborhoods': list(neighborhoods)
        }, status=status.HTTP_200_OK)
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