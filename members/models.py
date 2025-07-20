# members/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

CITY_CHOICES = [
    ('Istanbul', 'Istanbul'),
    ('Ankara', 'Ankara'),
    ('Izmir', 'Izmir'),
    # Add more as needed
]

ROLE_CHOICES = [
    ('member', 'Member'),
    ('admin', 'Admin'),
    ('superadmin', 'Super Admin'),
]

class User(AbstractUser):
    city = models.CharField(max_length=100, choices=CITY_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    def __str__(self):
        return f"{self.username} ({self.city})"

