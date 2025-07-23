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
    phone = models.CharField(max_length=15, blank=True, null=True, unique=True)
    city = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  # Use email as the username field
    REQUIRED_FIELDS = ['username']  # Include username since it's still part of AbstractUser

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

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

    class Meta:
        db_table = 'members_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'