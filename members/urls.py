# saha-backend/members/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('user/', views.user_detail, name='user_detail'),  # Added user detail endpoint
]
