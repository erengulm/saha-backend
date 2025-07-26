# urls.py (in your app urls.py - NOT the main project urls.py)
from django.urls import path
from . import views

urlpatterns = [
    # CSRF token endpoint
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),

    # Authentication endpoints - Removed api/ prefix since it's already in main urls.py
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_user, name='register'),

    # User profile endpoints
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/profile/update/', views.update_user_profile, name='update_user_profile'),
    path('user/change-password/', views.change_user_password, name='change_user_password'),

    # Admin endpoints
    path('users/', views.get_users_by_role, name='get_users_by_role'),
    path('users/<int:user_id>/role/', views.change_user_role, name='change_user_role'),

    # Keep your existing endpoint for backward compatibility
    path('user/', views.user_detail, name='user_detail'),
    path('users/by-city/', views.get_users_by_city, name='get_users_by_city'),
    path('debug/cities/', views.debug_cities, name='debug_cities'),
]