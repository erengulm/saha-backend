# members/views.py

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, UserUpdateSerializer, ChangePasswordSerializer
import json

User = get_user_model()


@api_view(['GET'])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Get CSRF token for frontend"""
    token = get_token(request)
    return JsonResponse({'csrfToken': token, 'message': 'CSRF cookie set'})

@api_view(['POST'])
def login_view(request):
    """Login with email and password"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        # Validation
        if not email or not password:
            return Response({
                'success': False,
                'error': 'E-posta ve şifre gereklidir'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Clean email
        email = email.strip().lower()

        # Try to find user by email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Geçersiz e-posta veya şifre'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return Response({
                'success': True,
                'message': 'Giriş başarılı',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Geçersiz e-posta veya şifre'
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'Giriş sırasında bir hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def logout_view(request):
    """Logout user"""
    logout(request)
    return Response({
        'success': True,
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request):
    """Get current user details"""
    user = request.user
    return Response({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'city': getattr(user, 'city', ''),
        'ilce': getattr(user, 'ilce', ''),
        'mahalle': getattr(user, 'mahalle', ''),
        'phone': getattr(user, 'phone', ''),
        'email': user.email,
        'role': getattr(user, 'role', None),
    })


@api_view(['POST'])
def register_user(request):
    """
    Registration field order for frontend (aligned with React RegisterPage):
    1. username (Will be split into first_name and last_name or used as display name)
    2. email (E-mail - will be used as username for authentication)
    3. phone (Telefon)
    4. city (Yaşadığınız şehir)
    5. password (Şifre)
    6. confirm_password (Şifre tekrar)
    7. role (defaults to 'member')
    """

    # Extract data from request
    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()
    email = request.data.get('email', '').strip().lower()
    phone = request.data.get('phone', '').strip()
    city = request.data.get('city', '').strip()
    ilce = request.data.get('ilce', '').strip()
    mahalle = request.data.get('mahalle', '').strip()
    password = request.data.get('password', '')
    confirm_password = request.data.get('confirm_password', '')
    role = request.data.get('role', 'member')

    # Validation errors dictionary
    errors = {}

    # Basic field validation
    if not first_name:
        errors['first_name'] = ['Ad gereklidir']
    elif len(first_name) < 2:
        errors['first_name'] = ['Ad en az 2 karakter olmalıdır']

    if not last_name:
        errors['last_name'] = ['Soyad gereklidir']
    elif len(last_name) < 2:
        errors['last_name'] = ['Soyad en az 2 karakter olmalıdır']

    if not email:
        errors['email'] = ['E-posta adresi gereklidir']
    elif User.objects.filter(email=email).exists():
        errors['email'] = ['Bu e-posta adresi ile kayıtlı bir kullanıcı zaten mevcut']

    if not phone:
        errors['phone'] = ['Telefon numarası gereklidir']
    elif User.objects.filter(phone=phone).exists():
        errors['phone'] = ['Bu telefon numarası ile kayıtlı bir kullanıcı zaten mevcut']

    if not city:
        errors['city'] = ['Şehir bilgisi gereklidir']

    if not ilce:
        errors['ilce'] = ['İlçe bilgisi gereklidir']

    if not mahalle:
        errors['mahalle'] = ['Mahalle bilgisi gereklidir']

    if not password:
        errors['password'] = ['Şifre gereklidir']
    elif len(password) < 8:
        errors['password'] = ['Şifre en az 8 karakter olmalıdır']

    if not confirm_password:
        errors['confirm_password'] = ['Şifre tekrarı gereklidir']
    elif password != confirm_password:
        errors['confirm_password'] = ['Şifreler eşleşmiyor']

    if role not in ['superadmin', 'admin', 'member']:
        errors['role'] = ['Geçersiz rol']

    # Return validation errors if any
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Prepare data for serializer
        serializer_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'city': city,
            'ilce': ilce,
            'mahalle': mahalle,
            'password': password,
            'confirm_password': confirm_password,
            'role': role
        }

        # Use serializer for final validation and creation
        serializer = UserRegistrationSerializer(data=serializer_data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'user_id': user.id,
                'email': user.email,
                'username': f"{user.first_name} {user.last_name}".strip(),
                'role': user.role
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'general': ['Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user's profile"""
    user = request.user
    return Response({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': f"{user.first_name} {user.last_name}".strip(),
        'city': user.city,
        'ilce': getattr(user, 'ilce', ''),
        'mahalle': getattr(user, 'mahalle', ''),
        'finansal_kod_numarasi': getattr(user, 'finansal_kod_numarasi', ''),
        'phone': getattr(user, 'phone', ''),
        'email': user.email,
    'meslegim': getattr(user, 'meslegim', ''),
    'ilgi_alanlarim': getattr(user, 'ilgi_alanlarim', ''),
        'yeteneklerim': getattr(user, 'yeteneklerim', ''),
        'hobilerim': getattr(user, 'hobilerim', ''),
        'role': user.role,
        'role_display': user.get_role_display(),
        'is_superadmin': user.is_superadmin,
        'is_admin': user.is_admin,
        'is_member': user.is_member,
        'has_admin_privileges': user.has_admin_privileges(),
        'created_at': user.created_at,
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update current user's profile"""
    user = request.user
    
    # Debug: Print received data
    print(f"DEBUG: Received profile update data: {request.data}")
    print(f"DEBUG: User being updated: {user.email}")

    # Handle username field if provided (split into first_name and last_name)
    if 'username' in request.data:
        username = request.data['username'].strip()
        name_parts = username.split(' ', 1)
        request.data['first_name'] = name_parts[0]
        request.data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
        # Remove username from data as it's not a model field
        request.data.pop('username', None)

    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    
    # Debug: Print serializer validation
    print(f"DEBUG: Serializer is_valid: {serializer.is_valid()}")
    if not serializer.is_valid():
        print(f"DEBUG: Serializer errors: {serializer.errors}")

    if serializer.is_valid():
        updated_user = serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': updated_user.id,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'username': f"{updated_user.first_name} {updated_user.last_name}".strip(),
                'city': updated_user.city,
                'ilce': getattr(updated_user, 'ilce', ''),
                'mahalle': getattr(updated_user, 'mahalle', ''),
                'finansal_kod_numarasi': getattr(updated_user, 'finansal_kod_numarasi', ''),
                'phone': getattr(updated_user, 'phone', ''),
                'email': updated_user.email,
                'meslegim': getattr(updated_user, 'meslegim', ''),
                'ilgi_alanlarim': getattr(updated_user, 'ilgi_alanlarim', ''),
                'yeteneklerim': getattr(updated_user, 'yeteneklerim', ''),
                'hobilerim': getattr(updated_user, 'hobilerim', ''),
                'role': updated_user.role,
                'role_display': updated_user.get_role_display(),
            }
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_user_password(request):
    """Change current user's password"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_by_role(request):
    """Get users filtered by role - only for admin and superadmin"""
    if not request.user.has_admin_privileges():
        return Response(
            {'error': 'Permission denied. Admin privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )

    role_filter = request.GET.get('role', None)

    if role_filter:
        users = User.objects.filter(role=role_filter)
    else:
        users = User.objects.all()

    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': f"{user.first_name} {user.last_name}".strip(),
            'city': user.city,
            'ilce': getattr(user, 'ilce', ''),
            'mahalle': getattr(user, 'mahalle', ''),
            'phone': getattr(user, 'phone', ''),
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'created_at': user.created_at,
            'is_active': user.is_active,
        })

    return Response({
        'users': users_data,
        'total_count': len(users_data),
        'role_counts': {
            'superadmin': User.objects.filter(role='superadmin').count(),
            'admin': User.objects.filter(role='admin').count(),
            'member': User.objects.filter(role='member').count(),
        }
    })


@api_view(['GET'])
def get_users_by_city(request):
    """Get users grouped by city for map display"""
    try:
        # Get all users with their cities and districts
        users = User.objects.filter(is_active=True).values('first_name', 'last_name', 'city', 'ilce', 'role')

        # Group users by city and district
        city_users = {}

        for user in users:
            city = user['city'].strip() if user['city'] else ''
            ilce = user['ilce'].strip() if user['ilce'] else ''
            
            if not city:
                continue

            full_name = f"{user['first_name']} {user['last_name']}".strip()

            # For Istanbul, group by district (ilce)
            # Use Turkish locale-aware comparison for Istanbul
            city_lower = city.replace('İ', 'i').replace('I', 'ı').lower()
            if city_lower == 'istanbul' and ilce:
                # Use district as the key for Istanbul
                if ilce not in city_users:
                    city_users[ilce] = []
                
                city_users[ilce].append({
                    'name': full_name,
                    'role': user['role']
                })
            else:
                # For other cities, group by city
                if city not in city_users:
                    city_users[city] = []

                city_users[city].append({
                    'name': full_name,
                    'role': user['role']
                })

        return Response({
            'success': True,
            'data': city_users,
            'total_cities': len(city_users),
            'total_users': sum(len(users) for users in city_users.values())
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'Kullanıcı verileri alınırken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_user_role(request, user_id):
    """Change a user's role - only superadmin can do this"""
    if not request.user.is_superadmin:
        return Response(
            {'error': 'Permission denied. Superadmin privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    new_role = request.data.get('role')
    if new_role not in ['superadmin', 'admin', 'member']:
        return Response(
            {'error': 'Invalid role. Must be superadmin, admin, or member.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prevent users from changing their own role
    if user.id == request.user.id:
        return Response(
            {'error': 'You cannot change your own role.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_role = user.role
    user.role = new_role

    # Update Django permissions based on role
    if new_role in ['superadmin', 'admin']:
        user.is_staff = True
    else:
        user.is_staff = False

    if new_role == 'superadmin':
        user.is_superuser = True
    else:
        user.is_superuser = False

    user.save()

    return Response({
        'message': f'User role changed from {old_role} to {new_role}',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': f"{user.first_name} {user.last_name}".strip(),
            'role': user.role,
            'role_display': user.get_role_display(),
        }
    }, status=status.HTTP_200_OK)