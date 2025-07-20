"""saha_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# saha-backend/saha_api/urls.py

# saha_api/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('members.urls')),

]


"""
from django.contrib import admin
from django.urls import path, include
from members import views as member_views
from members.views import csrf_token_view  # assuming you defined this



urlpatterns = [
    path('admin/', admin.site.urls),

    # CSRF Token Endpoint
    path('api/csrf/', csrf_token_view, name='csrf-token'),

    # Auth Endpoints
    path('api/register/', member_views.RegisterView.as_view(), name='register'),
    path('api/login/', member_views.LoginView.as_view(), name='login'),
    path('api/logout/', member_views.LogoutView.as_view(), name='logout'),

    # Other app-specific endpoints
    path('api/', include('members.urls')),
]
"""