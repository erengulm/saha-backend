# members/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    # Add these helper properties for your views
    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_member(self):
        return self.role == 'member'

    def has_admin_privileges(self):
        return self.role in ['superadmin', 'admin']