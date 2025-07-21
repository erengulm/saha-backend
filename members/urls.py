# saha-backend/members/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_detail, name='user_detail'),  # Added user detail endpoint
    path('register/', views.register_user, name='register'),
    path('profile/', views.user_profile, name='user_profile'),
    path('users/', views.get_users_by_role, name='get_users_by_role'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
]
