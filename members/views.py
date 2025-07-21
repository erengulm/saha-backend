from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer

User = get_user_model()

@api_view(['GET'])
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'message': 'CSRF cookie set'})

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({'message': 'Login successful', 'username': user.username})
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request):
    user = request.user
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'role': getattr(user, 'role', None),
        'city': getattr(user, 'city', None),
    })


@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user's profile"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'city': user.city,
        'role': user.role,
        'role_display': user.get_role_display(),
        'is_superadmin': user.is_superadmin,
        'is_admin': user.is_admin,
        'is_member': user.is_member,
        'has_admin_privileges': user.has_admin_privileges(),
        'created_at': user.created_at,
    })


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
            'username': user.username,
            'email': user.email,
            'city': user.city,
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
            'username': user.username,
            'role': user.role,
            'role_display': user.get_role_display(),
        }
    })
